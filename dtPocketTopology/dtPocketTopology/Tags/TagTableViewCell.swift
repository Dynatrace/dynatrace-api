//
//  TagTableViewCell.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 3/2/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit

class TagTableViewCell: UITableViewCell {
    @IBOutlet weak var displayName:         UILabel!
    @IBOutlet weak var entId:               UILabel!
    @IBOutlet weak var entType:             UILabel!
    @IBOutlet weak var hostButton:          TagUIButton!
    @IBOutlet weak var applicationButton:   TagUIButton!
    @IBOutlet weak var serviceButton:       TagUIButton!
    @IBOutlet weak var processGroupButton:  TagUIButton!
    @IBOutlet weak var processButton:       TagUIButton!
    
    override func awakeFromNib() {
        super.awakeFromNib()
        // Initialization code
    }

    override func setSelected(_ selected: Bool, animated: Bool) {
        super.setSelected(selected, animated: animated)

        // Configure the view for the selected state
    }

}
