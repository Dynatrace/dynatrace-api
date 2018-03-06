//
//  HostTableViewCell.swift
//  
//
//  Created by Hocker, Lucas on 1/30/18.
//

import UIKit

class HostTableViewCell: UITableViewCell {

    @IBOutlet weak var hostname: UILabel!
    @IBOutlet weak var osType: UILabel!
    var entityId = ""


    @IBOutlet weak var osSolarisImg: UIImageView!
    @IBOutlet weak var osAIXImg: UIImageView!
    @IBOutlet weak var osWinImg: UIImageView!
    @IBOutlet weak var osLinuxImg: UIImageView!
    
    override func prepareForReuse() {
        osSolarisImg.isHidden=true
        osAIXImg.isHidden=true
        osWinImg.isHidden=true
        osLinuxImg.isHidden=true
        osType.isHidden=true
        hostname.text=""
        entityId=""
    }
}
