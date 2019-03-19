var appservice = Class.create();
appservice.prototype = Object.extendsObject(global.AbstractAjaxProcessor, {
	
	/*
	* process the input JSON. Create or udpate a service and populate it with CIs
	*/
	processJSON_manualService: function (body) {

		var createOrUpdateServiceHandler = new CreateOrUpdateITService();	
		var json = "";
		var bsid = "";
		var errorId = "";
		var infoMessage = "";
		var responseObj = {};
		var manualEpBeforeChange;

		if (typeof createOrUpdateServiceHandler.processJSON === "function") {
			gs.log("using local instance method");
			return createOrUpdateServiceHandler.processJSON(body);
		}

		gs.log("using proprietary method");

		var bsm = new SNC.BusinessServiceManager();

		try {
			json = body;
			
			var bsName = json.name;
			if (bsName == '') {
				msg = gs.getMessage("Wrong input for creation or update of a service, The business service name must not be empty");	
			}
			
			// Insert or update the business service record
			if (msg === "") {
				var bsGr = new GlideRecord('cmdb_ci_service_discovered');
				bsGr.addQuery('name', bsName);
				bsGr.query();
				if (bsGr.next()) {
					// Validate the service_type is manual or empty
					gs.log('service type = ' + bsGr.service_type);
					if (bsGr.type == '2') {
						createOrUpdateServiceHandler.throwError(gs.getMessage("This API is allowed to operate only on empty or manual service. This service contains discovered elements"));
					}       
					createOrUpdateServiceHandler.populateServiceFields(bsGr, json);
					bsGr.update();
					bsId = bsGr.getUniqueValue();
				} else {
					createOrUpdateServiceHandler.populateServiceFields(bsGr, json);
					bsId = bsGr.insert();
					if (!bsId) {
						createOrUpdateServiceHandler.throwError(gs.getMessage("Failed to insert a new business service. Insertion was probably blocked by business rule"));
					}
				}
			
				var responseString = '/api/now/table/cmdb_ci_service_discovered/' + bsId;
				responseObj['url'] = responseString;
				responseObj['sys_id'] = bsId;
				responseObj['getContentUrl'] = '/api/now/cmdb/app_service/' + bsId + "/getContent";
			}
		
			var cisAdded = {};
			var relationsAdded = {};
								
			// Collect the manual endpoints in the service before the change
			manualEpBeforeChange = createOrUpdateServiceHandler.getManualEndpointsInService(bsId);

			// Iterate over relations
			var rels = json['service_relations'];
			var somethingChanged = true;
			if (rels) {
				for (var level = 0; level < 100 && somethingChanged; level++) {
					somethingChanged = false;
					for (var i = 0;i<rels.length ; i++) {
						var rel = rels[i];
						var parent = rel['parent'];
						if (!parent)
							parent = '';
						var child = rel['child'];
						var relKey = createOrUpdateServiceHandler.createRelationKey(rel);
						if (relationsAdded[relKey]) // we already handled this relation
							continue;
						if (!parent) { // this is an entry point
							msg = bsm.addCI(bsId, parent, child);
							if (msg) {
                                                                gs.print(msg);
								throw new sn_ws_err.BadRequestError(msg); 
                                                        }

							somethingChanged = true;
							cisAdded[child] = true;
							relationsAdded[relKey] = true;
							continue;
						}
						// If the parent was already added, we can add the child
						if (cisAdded[parent]) {
							msg = bsm.addCI(bsId, parent, child);
							if (msg)
								throw new sn_ws_err.BadRequestError(msg);
							cisAdded[child] = true;
							relationsAdded[relKey] = true;
							continue;
						}
					} // end of loop on relations
				} // end of loop over levels
		    
				// Check for dangling relations
				for (var j = 0;j < rels.length ; j++) {
					var rel1 = rels[j];
					var relKey1 = createOrUpdateServiceHandler.createRelationKey(rel1);
					if (!relationsAdded[relKey1]) 
						createOrUpdateServiceHandler.throwError(gs.getMessage('Relation from parent {0} to child {1} is dangling. The parent is not part of the service', [rel1['parent'], rel1['child']]));
				}

			} // End of handle relations
		
			// Remove endpoints if needed
			createOrUpdateServiceHandler.removeOutdatedManualEndpoints(manualEpBeforeChange, relationsAdded);
			
			// Report on the number of CIs added to the service
			var ciCount = 0;
			for (var ci in cisAdded) ciCount++;
			infoMessage = gs.getMessage('{0} CIs added to business service', ciCount + '');
			responseObj['info'] = infoMessage;
			
		}catch (e){
			msg = gs.getMessage("Add or create service failed: {0}", msg);
		}
		
		if (msg !== "") {
                        gs.print(msg);
			throw new sn_ws_err.BadRequestError(msg);
		}

		return responseObj;
	}
});
