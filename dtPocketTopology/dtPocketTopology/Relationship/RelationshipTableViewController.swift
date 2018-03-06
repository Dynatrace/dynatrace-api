//
//  RelationshipTableViewController.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 2/3/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit
import SwiftyJSON

class RelationshipTableViewController: UITableViewController {
    var type = ""
    var entityId = ""
    var ent: (Any)? = nil
//    var fromEntIds: [String] = [""]
//    var toEntIds: [String] = [""]
    var from:       JSON = JSON.null
    var to:         JSON = JSON.null
    var fromEnts:   [String : String] = [:]  //key:type
    var toEnts:     [String : String] = [:]  //key:type
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Uncomment the following line to preserve selection between presentations
        // self.clearsSelectionOnViewWillAppear = false

        // Uncomment the following line to display an Edit button in the navigation bar for this view controller.
        // self.navigationItem.rightBarButtonItem = self.editButtonItem
        
        switch(type){
        case "Host":
            from = topo.Hosts[entityId]!.json["fromRelationships"]
            to = topo.Hosts[entityId]!.json["toRelationships"]
        case "Process":
            from = topo.Processes[entityId]!.json["fromRelationships"]
            to = topo.Processes[entityId]!.json["toRelationships"]
        case "ProcessGroup":
            from = topo.ProcessGroups[entityId]!.json["fromRelationships"]
            to = topo.ProcessGroups[entityId]!.json["toRelationships"]
        case "Service":
            from = topo.Services[entityId]!.json["fromRelationships"]
            to = topo.Services[entityId]!.json["toRelationships"]
        case "Application":
            from = topo.Applications[entityId]!.json["fromRelationships"]
            to = topo.Applications[entityId]!.json["toRelationships"]
        default:
            entityId=""
            print("Not sure how I got here... unknown type")
        }
        
        if( !from.isEmpty) {
            for (k1,v1) in from {
                for (_,v2) in v1 {
                    fromEnts[v2.stringValue] = k1
                }
            }
        }
        if( !to.isEmpty) {
            for (k1,v1) in to {
                for (_,v2) in v1 {
                    toEnts[v2.stringValue] = k1
                }
            }
        }
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }

    // MARK: - Table view data source

    override func numberOfSections(in tableView: UITableView) -> Int {
        // #warning Incomplete implementation, return the number of sections
        return 2
    }

    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        switch(section){
        case 0:
            //return fromEntIds.count
            return fromEnts.count
        case 1:
            //return toEntIds.count
            return toEnts.count
         default:
            return 0
        }
    }

    
    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = self.tableView.dequeueReusableCell(withIdentifier: "relationshipCell", for: indexPath) as! RelationshipTableViewCell
        var keys: [(key: String, value: String)] = []
        var entId = ""
        
        // Configure the cell...
        switch(indexPath.section)
        {
        case 0:
            //let entId=fromEntIds[indexPath.row]
            keys = Array(fromEnts).sorted(by: {$0.1.lowercased() < $1.1.lowercased()})
            entId = keys[indexPath.row].key
            cell.relType.text = fromEnts[entId]
        case 1:
            //let entId=toEntIds[indexPath.row]
            keys = Array(toEnts).sorted(by: {$0.1.lowercased() < $1.1.lowercased()})
            entId = keys[indexPath.row].key
            cell.relType.text = toEnts[entId]
        default:
            cell.isHidden=true
        }
        
            //let entId = keys[indexPath.row].key
            let dash=entId.index(of: "-") ?? entId.endIndex
            let entType=entId[..<dash]
            cell.enType.text = String(entType)
            cell.entId.isHidden=true

            switch(entType)
            {
            case "HOST":
                cell.HostButton.setTitle(topo.Hosts[entId]?.displayName, for: .normal)
                cell.HostButton.isHidden=false
                cell.HostButton.entityId=entId
            case "PROCESS", "PROCESS_GROUP_INSTANCE":
                cell.ProcessButton.setTitle(topo.Processes[entId]?.displayName, for: .normal)
                cell.ProcessButton.isHidden=false
                cell.ProcessButton.entityId=entId
            case "PROCESS_GROUP":
                cell.ProcessGroupButton.setTitle(topo.ProcessGroups[entId]?.displayName, for: .normal)
                cell.ProcessGroupButton.isHidden=false
                cell.ProcessGroupButton.entityId=entId
            case "SERVICE":
                cell.ServiceButton.setTitle(topo.Services[entId]?.displayName, for: .normal)
                cell.ServiceButton.isHidden=false
                cell.ServiceButton.entityId=entId
            case "APPLICATION", "MOBILE_APPLICATION":
                cell.ApplicationButton.setTitle(topo.Applications[entId]?.displayName, for: .normal)
                cell.ApplicationButton.isHidden=false
                cell.ApplicationButton.entityId=entId
            default:
                //add display but disabled
                cell.entId.text = entId
                cell.entId.isHidden=false
                cell.datacenterButton.isHidden=false
                //cell.isHidden=true
                print("Unknown entType: \(entType), entId: \(entId)")
            }

        return cell
    }
    
    override func tableView(_ tableView: UITableView, titleForHeaderInSection section: Int) -> String? {
        switch(section){
        case 0:
            return "Relationship from:"
        case 1:
            return "Relationship to:"
        default:
            return ""
        }
    }

    /*
    // Override to support conditional editing of the table view.
    override func tableView(_ tableView: UITableView, canEditRowAt indexPath: IndexPath) -> Bool {
        // Return false if you do not want the specified item to be editable.
        return true
    }
    */

    /*
    // Override to support editing the table view.
    override func tableView(_ tableView: UITableView, commit editingStyle: UITableViewCellEditingStyle, forRowAt indexPath: IndexPath) {
        if editingStyle == .delete {
            // Delete the row from the data source
            tableView.deleteRows(at: [indexPath], with: .fade)
        } else if editingStyle == .insert {
            // Create a new instance of the appropriate class, insert it into the array, and add a new row to the table view
        }    
    }
    */

    /*
    // Override to support rearranging the table view.
    override func tableView(_ tableView: UITableView, moveRowAt fromIndexPath: IndexPath, to: IndexPath) {

    }
    */

    /*
    // Override to support conditional rearranging of the table view.
    override func tableView(_ tableView: UITableView, canMoveRowAt indexPath: IndexPath) -> Bool {
        // Return false if you do not want the item to be re-orderable.
        return true
    }
    */

    
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        let button = sender as? RelationshipUIButton
        switch(segue.identifier) {
        case "HostButtonSegue"?:
            if let destVC = segue.destination as? HostViewController {
                destVC.incomingEntityId=button!.entityId
            }
        case "ProcessButtonSegue"?:
        if let destVC = segue.destination as? ProcessViewController {
            destVC.incomingEntityId=button!.entityId
        }
        case "ProcessGroupSegue"?:
            if let destVC = segue.destination as? ProcessGroupViewController {
                destVC.incomingEntityId=button!.entityId
            }
        case "ServiceButtonSegue"?:
            if let destVC = segue.destination as? ServiceViewController {
                destVC.incomingEntityId=button!.entityId
            }
        case "ApplicationButtonSegue"?:
            if let destVC = segue.destination as? ApplicationViewController {
                destVC.incomingEntityId=button!.entityId
            }
        default:
            return
        }
    }

    
}
