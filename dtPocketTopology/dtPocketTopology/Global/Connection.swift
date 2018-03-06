//
//  Connection.swift
//  
//
//  Created by Hocker, Lucas on 1/31/18.
//

import Foundation
import SwiftKeychainWrapper

class myConnection {
  
    //Default vals
    var url = "https://XXXXXX.live.dynatrace.com/api/v1/"
    var token = "XXXXXXXXXXXXXXX"
    var email = "email@domain.com"
 
    
    var browserURL = ""
    var connected: Bool = false
    
    //let apiDG = DispatchGroup()
    
    init()
    {
        
    }
    
    func SaveToKeychain()
    {
        let urlSuccessful: Bool = KeychainWrapper.standard.set(url, forKey: "url")
        let tokenSuccessful: Bool = KeychainWrapper.standard.set(token, forKey: "token")
        let emailSuccessful: Bool = KeychainWrapper.standard.set(email, forKey: "email")
        if urlSuccessful && tokenSuccessful && emailSuccessful {
            print("Successful save to keychain.")
        } else {
            print("Unsuccessful save to keychain.")
        }
    }
    
    func GetFromKeychain() -> Bool {
        let urlString: String? = KeychainWrapper.standard.string(forKey: "url")
        let tokenString: String? = KeychainWrapper.standard.string(forKey: "token")
        let emailString: String? = KeychainWrapper.standard.string(forKey: "email")
        if (urlString != nil) && (tokenString != nil) && (tokenString != nil) && !(urlString!.isEmpty) && !(tokenString!.isEmpty) && !(emailString!.isEmpty) {
            self.url=urlString!
            self.token=tokenString!
            self.email=emailString!
            print("Successful load from keychain.")
            return true
        } else {
            print("Unsuccessful load from keychain.")
            return false
        }
    }
    
    func DeleteFromKeychain() -> Bool{
        return KeychainWrapper.standard.removeAllKeys()
    }
    
    func UpdateBrowserURL(){
        self.browserURL=myCon.url.replacingOccurrences(of: "api/v1/", with: "")
    }
}

let myCon = myConnection()


