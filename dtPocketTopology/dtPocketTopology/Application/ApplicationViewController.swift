//
//  ApplicationViewController.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 2/3/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit

class ApplicationViewController: UIViewController {

    @IBOutlet weak var displayName: UILabel!
    @IBOutlet weak var entityId: UILabel!
    @IBOutlet weak var applicationType: UILabel!
    var incomingEntityId = ""
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
        displayName.text=topo.Applications[incomingEntityId]?.displayName
        entityId.text=topo.Applications[incomingEntityId]?.entityId
        applicationType.text=topo.Applications[incomingEntityId]?.allplicationType
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
                destVC.type="Application"
            }
        }
        if segue.identifier == "jsonSegue"
        {
            if let destVC = segue.destination as? JSONViewController {
                destVC.entType="application"
                destVC.incomingEntId=self.incomingEntityId
            }
        }
    }
    
    @IBAction func openInBrowser(_ sender: Any) {
        //https://vvl663.managed-sprint.dynalabs.io/e/e6ac6c11-917a-46fa-9da3-55a7265f572f/#uemapplications/uemappmetrics;uemapplicationId=APPLICATION-EA7C4B59F27D43EB;gtf=l_72_HOURS
        //https://vvl663.managed-sprint.dynalabs.io/e/e6ac6c11-917a-46fa-9da3-55a7265f572f/#mobileappoverview;appId=MOBILE_APPLICATION-752C288D59734C79;gtf=l_72_HOURS
        //https://vvl663.managed-sprint.dynalabs.io/e/e6ac6c11-917a-46fa-9da3-55a7265f572f/#uemapplications/entity;id=APPLICATION-7324C7EE41CC3273;gtf=l_72_HOURS;visiblepart=
        //https://vvl663.managed-sprint.dynalabs.io/e/e6ac6c11-917a-46fa-9da3-55a7265f572f/#uemapplications/entity;id=DCRUM_APPLICATION-D2BBD7BF2D9E8587;gtf=l_72_HOURS
        let dash=self.incomingEntityId.index(of: "-") ?? self.incomingEntityId.endIndex
        let entType=String(self.incomingEntityId[..<dash])
        var url: URL? = nil
        
        switch(entType){
        case "APPLICATION":
            url = URL(string: "\(myCon.browserURL)#uemapplications/uemappmetrics;uemapplicationId=\(self.incomingEntityId);gtf=1_72_HOURS")
        case "MOBILE_APPLICATION":
            url = URL(string: "\(myCon.browserURL)#mobileappoverview;appId=\(self.incomingEntityId);gtf=1_72_HOURS")
        case "DCRUM_APPLICATION":
            url = URL(string: "\(myCon.browserURL)#uemapplications/entity;id=\(self.incomingEntityId);gtf=1_72_HOURS")
        default:
            return
        }
        UIApplication.shared.open(url!)
    }
    
}
