//
//  ProcessGroupViewController.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 2/6/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit

class ProcessGroupViewController: UIViewController {

    @IBOutlet weak var displayName: UILabel!
    @IBOutlet weak var entityId: UILabel!
    @IBOutlet weak var idCalcInputProps: UITextView!
    @IBOutlet weak var softwareTechnologies: UITextView!
    @IBOutlet weak var metadata: UITextView!
    var incomingEntityId = ""
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
        displayName.text=topo.ProcessGroups[incomingEntityId]?.displayName
        entityId.text=topo.ProcessGroups[incomingEntityId]?.entityId
        softwareTechnologies.text=topo.ProcessGroups[incomingEntityId]?
            .softwareTechnologies.rawString()
        metadata.text=topo.ProcessGroups[incomingEntityId]?.metadata.rawString()
        idCalcInputProps.text=topo.ProcessGroups[incomingEntityId]?.idCalcInputProps.rawString()
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
                destVC.type="ProcessGroup"
            }
        }
        if segue.identifier == "jsonSegue"
        {
            if let destVC = segue.destination as? JSONViewController {
                destVC.entType="processGroup"
                destVC.incomingEntId=self.incomingEntityId
            }
        }
    }
    @IBAction func openInBrowser(_ sender: Any) {
        let url = URL(string: "\(myCon.browserURL)#processgroupdetails;id=\(self.incomingEntityId);gtf=1_72_HOURS")
        UIApplication.shared.open(url!)
    }
}
