//
//  ServiceTableViewCell.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 2/1/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit

class ServiceTableViewCell: UITableViewCell {

    @IBOutlet weak var serviceName: UILabel!
    @IBOutlet weak var serviceType: UILabel!
    @IBOutlet weak var agentType: UILabel!
    var entityId = ""
    
    override func awakeFromNib() {
        super.awakeFromNib()
        // Initialization code
    }

    override func setSelected(_ selected: Bool, animated: Bool) {
        super.setSelected(selected, animated: animated)

        // Configure the view for the selected state
    }

}
