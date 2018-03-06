//
//  menuTableViewController.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 1/31/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit
import Alamofire

class menuTableViewController: UITableViewController {
    @IBOutlet weak var numApplications: UILabel!
    @IBOutlet weak var numServices: UILabel!
    @IBOutlet weak var numProcesses: UILabel!
    @IBOutlet weak var numHosts: UILabel!
    @IBOutlet weak var numProcessGroups: UILabel!
    @IBOutlet weak var numIPs: UILabel!
    @IBOutlet weak var numTags: UILabel!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
        self.loadTopology()
    }
    
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        switch(segue.identifier) {
        case "logoutSegue"?:
            if let destVC = segue.destination as? LoginViewController {
                myCon.connected=false
                topo=Topology()
                destVC.incomingMessage="Logged Out"
            }
        
        default:
            return
        }
    }

    func loadTopology()
    {
        topo.getJsonFromUrl(type: "Hosts", endpoint: "entity/infrastructure/hosts", menu: self)
        topo.getJsonFromUrl(type: "Processes", endpoint: "entity/infrastructure/processes", menu: self)
        topo.getJsonFromUrl(type: "ProcessGroups", endpoint: "entity/infrastructure/process-groups", menu: self)
        topo.getJsonFromUrl(type: "Services", endpoint: "entity/services", menu: self)
        topo.getJsonFromUrl(type: "Applications", endpoint: "entity/applications", menu: self)
    }
    
    @IBAction func refreshButton(_ sender: Any) {
        topo=Topology()
        numApplications.text=""
        numServices.text=""
        numProcesses.text=""
        numHosts.text=""
        numProcessGroups.text=""
        numIPs.text=""
        numTags.text=""
        self.loadTopology()
    }
}
