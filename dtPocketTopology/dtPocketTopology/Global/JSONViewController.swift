//
//  JSONViewController.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 3/5/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit

class JSONViewController: UIViewController {
    @IBOutlet weak var jsonText: UITextView!
    var entType = ""
    var incomingEntId = ""
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
        switch(entType){
        case "host":
            jsonText.text=topo.Hosts[incomingEntId]?.json.rawString()
        case "process":
            jsonText.text=topo.Processes[incomingEntId]?.json.rawString()
        case "processGroup":
            jsonText.text=topo.ProcessGroups[incomingEntId]?.json.rawString()
        case "service":
            jsonText.text=topo.Services[incomingEntId]?.json.rawString()
        case "application":
            jsonText.text=topo.Applications[incomingEntId]?.json.rawString()
        default:
            jsonText.text=""
        }
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destinationViewController.
        // Pass the selected object to the new view controller.
    }
    */

}
