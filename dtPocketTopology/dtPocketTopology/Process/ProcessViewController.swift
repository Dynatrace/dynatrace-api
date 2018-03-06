//
//  ProcessViewController.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 2/3/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit

class ProcessViewController: UIViewController {

    @IBOutlet weak var displayName: UILabel!
    @IBOutlet weak var entityId: UILabel!
    @IBOutlet weak var listenPorts: UILabel!
    @IBOutlet weak var softwareTechnologies: UITextView!
    @IBOutlet weak var metadata: UITextView!
    
    
    @IBOutlet weak var hostname: UIButton!
    var incomingEntityId = ""
    var hostEntityId = ""
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
        displayName.text=topo.Processes[incomingEntityId]?.displayName
        entityId.text=topo.Processes[incomingEntityId]?.entityId
        hostEntityId=topo.Processes[incomingEntityId]?.hostEntityId ?? ""
        hostname.setTitle(topo.Hosts[hostEntityId]?.displayName, for: .normal)
        listenPorts.text=topo.Processes[incomingEntityId]?
            .listenPorts.map(String.init).joined(separator: ", ") ?? ""
        softwareTechnologies.text=topo.Processes[incomingEntityId]?
            .softwareTechnologies.rawString()
        metadata.text=topo.Processes[incomingEntityId]?.metadata.rawString()
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
                destVC.type="Process"
            }
        }
        if segue.identifier == "processToHostSegue"
        {
            if let destVC = segue.destination as? HostViewController {
                destVC.incomingEntityId=self.hostEntityId
            }
        }
        if segue.identifier == "jsonSegue"
        {
            if let destVC = segue.destination as? JSONViewController {
                destVC.entType="process"
                destVC.incomingEntId=self.incomingEntityId
            }
        }
    }
    
    @IBAction func openInBrowser(_ sender: Any) {
        let url = URL(string: "\(myCon.browserURL)#processdetails;id=\(self.incomingEntityId);gtf=1_72_HOURS")
        UIApplication.shared.open(url!)
    }
    
}
