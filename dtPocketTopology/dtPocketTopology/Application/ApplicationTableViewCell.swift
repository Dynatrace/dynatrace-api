//
//  ApplicationTableViewCell.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 2/1/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit

class ApplicationTableViewCell: UITableViewCell {

    @IBOutlet weak var applicationName: UILabel!
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
