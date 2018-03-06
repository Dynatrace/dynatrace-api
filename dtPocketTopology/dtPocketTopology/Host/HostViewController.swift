//
//  HostViewController.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 2/2/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit

class HostViewController: UIViewController {

    @IBOutlet weak var displayName: UILabel!
    @IBOutlet weak var entityId: UILabel!
    @IBOutlet weak var osType: UILabel!
    @IBOutlet weak var osArchitecture: UILabel!
    @IBOutlet weak var osVersion: UILabel!
    @IBOutlet weak var hypervisorType: UILabel!
    @IBOutlet weak var ipAddresses: UILabel!
    var incomingEntityId = ""
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
        entityId.text=topo.Hosts[incomingEntityId]?.entityId
        displayName.text=topo.Hosts[incomingEntityId]?.displayName
        osType.text=topo.Hosts[incomingEntityId]?.osType
        osArchitecture.text=topo.Hosts[incomingEntityId]?.osArchitecture
        osVersion.text=topo.Hosts[incomingEntityId]?.osVersion
        osVersion.text=topo.Hosts[incomingEntityId]?.osVersion
        hypervisorType.text=topo.Hosts[incomingEntityId]?.hypervisorType
        ipAddresses.text=topo.Hosts[incomingEntityId]?.ipAddresses.joined(separator: ", ")
        ipAddresses.sizeToFit()
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
                destVC.type="Host"
            }
        }
        if segue.identifier == "jsonSegue"
        {
            if let destVC = segue.destination as? JSONViewController {
                destVC.entType="host"
                destVC.incomingEntId=self.incomingEntityId
            }
        }
    }
    
    @IBAction func openInBrowser(_ sender: Any) {
        let url = URL(string: "\(myCon.browserURL)#hosts/hostdetails;id=\(self.incomingEntityId);gtf=1_72_HOURS")
        UIApplication.shared.open(url!)
    }
    
}
