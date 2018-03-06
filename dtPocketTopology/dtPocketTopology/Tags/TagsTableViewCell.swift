//
//  TagsTableViewCell.swift
//  
//
//  Created by Hocker, Lucas on 3/1/18.
//

import UIKit

class TagsTableViewCell: UITableViewCell {

    @IBOutlet weak var tagLabel: UILabel!
    @IBOutlet weak var numTags: UILabel!

    override func awakeFromNib() {
        super.awakeFromNib()
        // Initialization code
    }

    override func setSelected(_ selected: Bool, animated: Bool) {
        super.setSelected(selected, animated: animated)

        // Configure the view for the selected state
    }

}
