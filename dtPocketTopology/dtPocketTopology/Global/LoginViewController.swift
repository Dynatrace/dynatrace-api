//
//  ViewController.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 1/29/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit
import Alamofire
import Dynatrace

class LoginViewController: UIViewController {
   
    @IBOutlet weak var urlField: UITextField!
    @IBOutlet weak var tokenField: UITextField!
    @IBOutlet weak var errorLabel: UILabel!
    @IBOutlet weak var connectButton: UIButton!
    @IBOutlet weak var email: UITextField!
    @IBOutlet weak var SaveToKeychain: UISwitch!
    var incomingMessage = ""
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.

        //Drop in a static connection for testing
        _ = myCon.GetFromKeychain()
        urlField.text=myCon.url
        tokenField.text=myCon.token
        email.text=myCon.email
        
        
        errorLabel.text=incomingMessage
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }

    override func shouldPerformSegue(withIdentifier identifier: String, sender: Any?) -> Bool {
        if(myCon.connected==true){
            return true
        } else {
            return false
        }
    }
    
    @IBAction func connectButton(_ sender: UIButton) {
        testConnection(sender, urlString: urlField.text!, tokenString: tokenField.text!)
    }

    //this function is fetching the json from URL
    func testConnection(_ sender: UIButton, urlString: String, tokenString: String){
        let url = "\(urlString)config/clusterversion"
        let headers: HTTPHeaders = [
            "Authorization": "Api-Token \(tokenString)"]
        
        
        Alamofire.request(
            url,
            method: .get,
            headers: headers)
            .validate(statusCode: 200..<300)
            .validate(contentType: ["application/json"])
            .responseJSON {
             response in
                switch response.result {
                case .success:
                    //let json = response.result.value
                    //print("JSON: \(json ?? "")")
                    myCon.connected=true
                    myCon.url=urlString
                    myCon.token=tokenString
                    myCon.email=self.email.text ?? ""
                    Dynatrace.identifyUser(self.email.text)
                    
                    if self.SaveToKeychain.isOn == true {
                        myCon.SaveToKeychain()
                    } else {
                        _ = myCon.DeleteFromKeychain()
                    }
                    
                    myCon.UpdateBrowserURL()
                    self.performSegue(withIdentifier: "loginSegue", sender: sender)
                case .failure:
                    myCon.connected=false
                    self.errorLabel.text="Response: \(String(describing: response.response))"
                }
             }
    }
    
    
}

