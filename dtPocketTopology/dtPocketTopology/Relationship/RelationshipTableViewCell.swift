//
//  RelationshipTableViewCell.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 2/3/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit

class RelationshipTableViewCell: UITableViewCell {

    @IBOutlet weak var HostButton: RelationshipUIButton!
    @IBOutlet weak var ProcessButton: RelationshipUIButton!
    @IBOutlet weak var ServiceButton: RelationshipUIButton!
    @IBOutlet weak var ApplicationButton: RelationshipUIButton!
    @IBOutlet weak var relType: UILabel!
    @IBOutlet weak var enType: UILabel!
    @IBOutlet weak var entId: UILabel!
    @IBOutlet weak var datacenterButton: RelationshipUIButton!
    @IBOutlet weak var ProcessGroupButton: RelationshipUIButton!
    
    override func awakeFromNib() {
        super.awakeFromNib()
        // Initialization code
    }

    override func setSelected(_ selected: Bool, animated: Bool) {
        super.setSelected(selected, animated: animated)

        // Configure the view for the selected state
    }
    
    override func prepareForReuse() {
        HostButton.entityId=""
        HostButton.setTitle("", for: .normal)
        HostButton.isHidden=true
        
        ProcessButton.entityId=""
        ProcessButton.setTitle("", for: .normal)
        ProcessButton.isHidden=true
        
        ProcessGroupButton.entityId=""
        ProcessGroupButton.setTitle("", for: .normal)
        ProcessGroupButton.isHidden=true
        
        ServiceButton.entityId=""
        ServiceButton.setTitle("", for: .normal)
        ServiceButton.isHidden=true
        
        ApplicationButton.entityId=""
        ApplicationButton.setTitle("", for: .normal)
        ApplicationButton.isHidden=true
        
        datacenterButton.isHidden=true
        
        relType.text=""
        enType.text=""
        entId.text=""
        entId.isHidden=true
    }

    @IBAction func openInBrowser(_ sender: Any) {
        //https://vvl663.managed-sprint.dynalabs.io/e/e6ac6c11-917a-46fa-9da3-55a7265f572f/#smartscape;layer=DATACENTERS;id=AZURE_REGION-F4FDC1868C659C90
        //https://vvl663.managed-sprint.dynalabs.io/e/e6ac6c11-917a-46fa-9da3-55a7265f572f/#smartscape;layer=DATACENTERS;id=OPENSTACK_REGION-05EA428E4F508D4B
        //https://vvl663.managed-sprint.dynalabs.io/e/e6ac6c11-917a-46fa-9da3-55a7265f572f/#smartscape;layer=DATACENTERS;id=GEOLOC_SITE-FAC9C9591DC19CA7
        //https://vvl663.managed-sprint.dynalabs.io/e/e6ac6c11-917a-46fa-9da3-55a7265f572f/#smartscape;layer=DATACENTERS;id=AWS_AVAILABILITY_ZONE-334F93507088AE03
        //https://vvl663.managed-sprint.dynalabs.io/e/e6ac6c11-917a-46fa-9da3-55a7265f572f/#rdsdetails;rdsId=RELATIONAL_DATABASE_SERVICE-5F5E84B8547457D1;gtf=l_72_HOURS
        //https://vvl663.managed-sprint.dynalabs.io/e/e6ac6c11-917a-46fa-9da3-55a7265f572f/#elbdetails;id=-5330241089690111104;elbId=ELASTIC_LOAD_BALANCER-057BA8946CE1E139;gtf=l_72_HOURS
        
        var urlS = ""
        let entType = self.enType.text ?? ""
        switch(entType){
        case "AZURE_REGION", "OPENSTACK_REGION", "GEOLOC_SITE":
            urlS = "\(myCon.browserURL)#smartscape;layer=DATACENTERS;id=\(self.entId.text!);gtf=1_72_HOURS"
        case "RELATIONAL_DATABASE_SERVICE":
            urlS = "\(myCon.browserURL)#rdsdetails;rdsId=\(self.entId.text!);gtf=1_72_HOURS"
        case "ELASTIC_LOAD_BALANCER":
            urlS = "\(myCon.browserURL)#elbdetails;id=\(self.entId.text!);gtf=1_72_HOURS"
        default:
            urlS = "\(myCon.browserURL)#smartscape;id=\(self.entId.text!);gtf=1_72_HOURS"
        }
        let url = URL(string: urlS)
        UIApplication.shared.open(url!)
    }
}
