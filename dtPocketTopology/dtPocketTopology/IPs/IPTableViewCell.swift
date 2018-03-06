//
//  IPTableViewCell.swift
//  
//
//  Created by Hocker, Lucas on 3/1/18.
//

import UIKit

class IPTableViewCell: UITableViewCell {

    @IBOutlet weak var ip: UILabel!
    @IBOutlet weak var hostname: UILabel!
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
