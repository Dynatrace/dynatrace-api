//
//  Model.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 1/30/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import Foundation
import UIKit
import Alamofire
import SwiftyJSON

class Host {
    var entityId:               String
    var displayName:            String
    var osType:                 String
    var osArchitecture:         String
    var osVersion:              String
    var hypervisorType:         String
    var ipAddresses:            [String]
    var fromNetworkClients:     [String]
    var toNetworkClients:       [String]
    var json:                   JSON
    
    init( subJSON: JSON ){
        self.entityId=subJSON["entityId"].stringValue
        self.displayName=subJSON["displayName"].stringValue
        self.osType=subJSON["osType"].stringValue
        self.osArchitecture=subJSON["osArchitecture"].stringValue
        self.osVersion=subJSON["osVersion"].stringValue
        self.hypervisorType=subJSON["hypervisorType"].stringValue
        self.ipAddresses=subJSON["ipAddresses"].arrayValue.map({$0.stringValue})
        self.fromNetworkClients=subJSON["fromRelationships"]["isNetworkClientOfHost"].arrayValue.map({$0.stringValue})
        self.toNetworkClients=subJSON["toRelationships"]["isNetworkClientOfHost"].arrayValue.map({$0.stringValue})

        var tag = ""
        for i in subJSON["tags"] {
            tag = i.1["key"].stringValue
            if i.1["context"].exists() && i.1["context"].stringValue != "CONTEXTLESS" {
                let context=i.1["context"].stringValue
                tag="[\(context)]\(tag)"
            }
            if i.1["value"].exists() {
                let value=i.1["value"].stringValue
                tag="\(tag):\(value)"
            }
            if topo.Tags[tag]?.isEmpty ?? true {
                topo.Tags[tag]=Array()
            }
            topo.Tags[tag]?.append(self.entityId)
        }
        
        var ip = ""
        for i in subJSON["ipAddresses"] {
            ip = i.1.stringValue

            if let host1 = topo.IPs[ip] {
                print("Duplicate IP: \(ip), host1: \(host1), host2: \(self.entityId)")
            } else
            {
                topo.IPs[ip] = self.entityId
            }
            
        }
        
        json=subJSON
    }
}

class Process {
    var entityId:               String
    var displayName:            String
    var hostEntityId:           String
    var listenPorts:            [Int]
    var softwareTechnologies:   JSON
    var fromNetworkClients:     [String]
    var toNetworkClients:       [String]
    var metadata:               JSON
    var json:                   JSON

    init( subJSON: JSON ){
        self.entityId=subJSON["entityId"].stringValue
        self.displayName=subJSON["displayName"].stringValue
        self.hostEntityId=subJSON["fromRelationships"]["isProcessOf"][0].stringValue
        self.listenPorts=subJSON["listenPorts"].arrayValue.map({$0.intValue})
        self.softwareTechnologies=subJSON["softwareTechnologies"]
        self.fromNetworkClients=subJSON["fromRelationships"]["isNetworkClientOf"].arrayValue.map({$0.stringValue})
        self.toNetworkClients=subJSON["toRelationships"]["isNetworkClientOf"].arrayValue.map({$0.stringValue})
        self.metadata=subJSON["metadata"]

        var tag = ""
        for i in subJSON["tags"] {
            tag = i.1["key"].stringValue
            if i.1["context"].exists() && i.1["context"].stringValue != "CONTEXTLESS" {
                let context=i.1["context"].stringValue
                tag="[\(context)]\(tag)"
            }
            if i.1["value"].exists() {
                let value=i.1["value"].stringValue
                tag="\(tag):\(value)"
            }
            if topo.Tags[tag]?.isEmpty ?? true {
                topo.Tags[tag]=Array()
            }
            topo.Tags[tag]?.append(self.entityId)
        }
        json=subJSON
    }
}

class ProcessGroup{
    var entityId:               String
    var displayName:            String
    var fromRunsOn:             [String]
    var toRunsOn:               [String]
    var idCalcInputProps:       JSON
    var metadata:               JSON
    var softwareTechnologies:   JSON
    var json:                   JSON
    var numPGIs:                Int=0
    
    init( subJSON: JSON ){
        self.entityId=subJSON["entityId"].stringValue
        self.displayName=subJSON["displayName"].stringValue
        self.softwareTechnologies=subJSON["softwareTechnologies"]
        self.fromRunsOn=subJSON["fromRelationships"]["runsOn"].arrayValue.map({$0.stringValue})
        self.toRunsOn=subJSON["toRelationships"]["runsOn"].arrayValue.map({$0.stringValue})
        self.numPGIs=subJSON["toRelationships"]["isInstanceOf"].count
        self.metadata=subJSON["metadata"]
        self.idCalcInputProps=subJSON["idCalcInputProps"]

        var tag = ""
        for i in subJSON["tags"] {
            tag = i.1["key"].stringValue
            if i.1["context"].exists() && i.1["context"].stringValue != "CONTEXTLESS" {
                let context=i.1["context"].stringValue
                tag="[\(context)]\(tag)"
            }
            if i.1["value"].exists() {
                let value=i.1["value"].stringValue
                tag="\(tag):\(value)"
            }
            if topo.Tags[tag]?.isEmpty ?? true {
                topo.Tags[tag]=Array()
            }
            topo.Tags[tag]?.append(self.entityId)
        }
        json=subJSON
    }
}

class Service{
    var entityId:               String
    var displayName:            String
    var serviceType:            String
    var agentTechnologyType:    String
    var serviceTechnologyTypes: [String]
    var webServiceName:         String
    var webServiceNamespace:    String
    var fromCalls:              [String]
    var toCalls:                [String]
    var json:                   JSON
    
    init( subJSON: JSON ){
        self.entityId=subJSON["entityId"].stringValue
        self.displayName=subJSON["displayName"].stringValue
        self.serviceType=subJSON["serviceType"].stringValue
        self.agentTechnologyType=subJSON["agentTechnologyType"].stringValue
        self.serviceTechnologyTypes=subJSON["serviceTechnologyTypes"].arrayValue.map({$0.stringValue})
        self.webServiceName=subJSON["webServiceName"].stringValue
        self.webServiceNamespace=subJSON["webServiceNamespace"].stringValue
        self.fromCalls=subJSON["fromRelationships"]["calls"].arrayValue.map({$0.stringValue})
        self.toCalls=subJSON["toRelationships"]["calls"].arrayValue.map({$0.stringValue})

        var tag = ""
        for i in subJSON["tags"] {
            tag = i.1["key"].stringValue
            if i.1["context"].exists() && i.1["context"].stringValue != "CONTEXTLESS" {
                let context=i.1["context"].stringValue
                tag="[\(context)]\(tag)"
            }
            if i.1["value"].exists() {
                let value=i.1["value"].stringValue
                tag="\(tag):\(value)"
            }
            if topo.Tags[tag]?.isEmpty ?? true {
                topo.Tags[tag]=Array()
            }
            topo.Tags[tag]?.append(self.entityId)
        }
        json=subJSON
    }
}

class Application{
    var entityId:           String
    var displayName:        String
    var allplicationType:   String
    var fromCalls:          [String]
    var toCalls:            [String] = [""]
    var json:                   JSON
    
    init( subJSON: JSON ){
        self.entityId=subJSON["entityId"].stringValue
        self.displayName=subJSON["displayName"].stringValue
        self.fromCalls=subJSON["fromRelationships"]["calls"].arrayValue.map({$0.stringValue})
        self.allplicationType=subJSON["applicationType"].stringValue

        var tag = ""
        for i in subJSON["tags"] {
            tag = i.1["key"].stringValue
            if i.1["context"].exists() && i.1["context"].stringValue != "CONTEXTLESS" {
                let context=i.1["context"].stringValue
                tag="[\(context)]\(tag)"
            }
            if i.1["value"].exists() {
                let value=i.1["value"].stringValue
                tag="\(tag):\(value)"
            }
            if topo.Tags[tag]?.isEmpty ?? true {
                topo.Tags[tag]=Array()
            }
            topo.Tags[tag]?.append(self.entityId)
        }
        json=subJSON
    }
}

class Topology{
    var Applications:   [String: Application] = [:]
    var Services:       [String: Service] = [:]
    var ProcessGroups:  [String: ProcessGroup] = [:]
    var Processes:      [String: Process] = [:]
    var Hosts:          [String: Host] = [:]
    var Tags:           [String: [String]] = [:]
    var IPs:            [String: String] = [:]
    
    var debugEntTypes:  [String: Bool] = [:]
    
    //this function is fetching the json from URL
    func getJsonFromUrl(type: String, endpoint: String, menu: menuTableViewController){
        var entityId: String = ""
        let url = "\(myCon.url)\(endpoint)"
        let headers: HTTPHeaders = [
            "Authorization": "Api-Token \(myCon.token)"]
        Alamofire.request(
            url,
            method: .get,
            headers: headers
            )
            .validate(statusCode: 200..<300)
            .validate(contentType: ["application/json"])
            .responseJSON{
                response in
                switch response.result {
                case .success:
                    let json = JSON(response.result.value!)
                    //print("JSON: \(json ?? "")")
                    
                    //Load the hosts model
                    for (_,subJson):(String,JSON) in json {
                        entityId=subJson["entityId"].stringValue
                        switch(type){
                        case "Hosts":
                            topo.Hosts[entityId] = Host(subJSON: subJson)
                            for i in topo.Hosts {
                                let dash=i.key.index(of: "-") ?? i.key.endIndex
                                let entType=i.key[..<dash]
                                let type = String("Host:\(entType)")
                                topo.debugEntTypes[type] = true
                            }
                        case "Processes":
                            topo.Processes[entityId] = Process(subJSON: subJson)
                            for i in topo.Processes {
                                let dash=i.key.index(of: "-") ?? i.key.endIndex
                                let entType=i.key[..<dash]
                                let type = String("Process:\(entType)")
                                topo.debugEntTypes[type] = true
                            }
                        case "ProcessGroups":
                            topo.ProcessGroups[entityId] = ProcessGroup(subJSON: subJson)
                            for i in topo.ProcessGroups {
                                let dash=i.key.index(of: "-") ?? i.key.endIndex
                                let entType=i.key[..<dash]
                                let type = String("ProcessGroup:\(entType)")
                                topo.debugEntTypes[type] = true
                            }
                        case "Services":
                            topo.Services[entityId] = Service(subJSON: subJson)
                            for i in topo.Services {
                                let dash=i.key.index(of: "-") ?? i.key.endIndex
                                let entType=i.key[..<dash]
                                let type = String("Service:\(entType)")
                                topo.debugEntTypes[type] = true
                            }
                        case "Applications":
                            topo.Applications[entityId] = Application(subJSON: subJson)
                            for i in topo.Applications {
                                let dash=i.key.index(of: "-") ?? i.key.endIndex
                                let entType=i.key[..<dash]
                                let type = String("Application:\(entType)")
                                topo.debugEntTypes[type] = true
                            }
                        default:
                            print(subJson)
                        }
                    }
                    switch(type){
                    case "Hosts":
                        menu.numHosts.text=String(topo.Hosts.count)
                        menu.numIPs.text=String(topo.IPs.count)
                        menu.numTags.text=String(topo.Tags.count)
                    case "Processes":
                        menu.numProcesses.text=String(topo.Processes.count)
                        menu.numTags.text=String(topo.Tags.count)
                    case "ProcessGroups":
                        menu.numProcessGroups.text=String(topo.ProcessGroups.count)
                        menu.numTags.text=String(topo.Tags.count)
                    case "Services":
                        menu.numServices.text=String(topo.Services.count)
                        menu.numTags.text=String(topo.Tags.count)
                    case "Applications":
                        menu.numApplications.text=String(topo.Applications.count)
                        menu.numTags.text=String(topo.Tags.count)
                    default:
                        print("Unknown how to load \(type).")
                    }
                    
                case .failure:
                    print("\(endpoint) failed: \n")
                    print("Request: \(String(describing: response.request))")   // original url request
                    print("Response: \(String(describing: response.response))") // http url response
                    print("Result: \(response.result)")                         // response serialization result
                }
                
                
        }
    }
}

var topo = Topology()
