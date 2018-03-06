//
//  ServiceViewController.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 2/3/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit

class ServiceViewController: UIViewController {

    @IBOutlet weak var displayName: UILabel!
    @IBOutlet weak var entityId: UILabel!
    @IBOutlet weak var serviceType: UILabel!
    @IBOutlet weak var agentTechnology: UILabel!
    @IBOutlet weak var webServiceName: UILabel!
    @IBOutlet weak var namespace: UILabel!
    @IBOutlet weak var serviceTechnologyType: UILabel!
    var incomingEntityId = ""
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
        entityId.text=topo.Services[incomingEntityId]?.entityId
        displayName.text=topo.Services[incomingEntityId]?.displayName
        serviceType.text=topo.Services[incomingEntityId]?.serviceType
        agentTechnology.text=topo.Services[incomingEntityId]?.agentTechnologyType
        webServiceName.text=topo.Services[incomingEntityId]?.webServiceName
        namespace.text=topo.Services[incomingEntityId]?.webServiceNamespace
        serviceTechnologyType.text=topo.Services[incomingEntityId]?.serviceTechnologyTypes.joined(separator: ", ")
        serviceTechnologyType.sizeToFit()
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    

    
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destinationViewController.
        // Pass the selected object to the new view controller.
        if segue.identifier == "relationshipSegue"
        {
            if let destVC = segue.destination as? RelationshipTableViewController {
                destVC.entityId=self.entityId.text ?? ""
                destVC.type="Service"
            }
        }
        if segue.identifier == "jsonSegue"
        {
            if let destVC = segue.destination as? JSONViewController {
                destVC.entType="service"
                destVC.incomingEntId=self.incomingEntityId
            }
        }
    }
    
    @IBAction func openInBrowser(_ sender: Any) {
        let url = URL(string: "\(myCon.browserURL)#services/serviceOverview;id=\(self.incomingEntityId);gtf=1_72_HOURS")
        UIApplication.shared.open(url!)
    }
    
}
