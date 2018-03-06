//
//  ProcessGroupTableViewCell.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 2/6/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit

class ProcessGroupTableViewCell: UITableViewCell {

    @IBOutlet weak var processGroupName: UILabel!
    @IBOutlet weak var numPGI: UILabel!
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
