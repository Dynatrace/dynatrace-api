//
//  HostsTableViewController.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 1/31/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit
import Alamofire

class HostsTableViewController: UITableViewController, UISearchResultsUpdating, UISearchBarDelegate {
    
    let searchController = UISearchController(searchResultsController: nil)
    var hostList: [String: String] = [:]
    var filteredHosts: [String: String] = [:]
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
        //print("HostTableViewController: \(topo.Hosts.count)")
        
        searchController.searchResultsUpdater = self
        tableView.tableHeaderView = searchController.searchBar
        searchController.hidesNavigationBarDuringPresentation = false
        searchController.dimsBackgroundDuringPresentation = false
        for (entId,host) in topo.Hosts {
            hostList[entId] = host.displayName
        }
        filteredHosts=hostList
    }
    
    override func numberOfSections(in tableView: UITableView) -> Int {
        return 1
    }
    
    override func tableView(_ tableView: UITableView, numberOfRowsInSection: Int) -> Int {
        return filteredHosts.count
    }
    
    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let keys = Array(filteredHosts).sorted(by: {$0.1.lowercased() < $1.1.lowercased()})
        let cellIdentifier = "hostCell"
        let cell = self.tableView.dequeueReusableCell(withIdentifier: cellIdentifier, for: indexPath) as! HostTableViewCell
        let key = keys[indexPath.row].key
        let host = topo.Hosts[key]
        cell.hostname.text = host!.displayName
        cell.osType.text = host!.osType
        cell.entityId = host!.entityId
        switch(host!.osType){
        case "LINUX":
            cell.osLinuxImg.isHidden=false
        case "WINDOWS":
            cell.osWinImg.isHidden=false
        case "AIX":
            cell.osAIXImg.isHidden=false
        case "SOLARIS":
            cell.osSolarisImg.isHidden=false
        default:
            cell.osType.isHidden=false
        }
        
        return cell
    }
    
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        if segue.identifier == "hostSegue"
        {
            if let destVC = segue.destination as? HostViewController {
                let cell = sender as? HostTableViewCell
                destVC.incomingEntityId=cell!.entityId
            }
        }
        
    }
    
    func updateSearchResults(for searchController: UISearchController) {
        if let searchText = searchController.searchBar.text {
            if !searchText.isEmpty {
                filteredHosts = hostList.filter { (key,val) in
                    return val.lowercased().contains(searchText.lowercased())
                }
                
            }
        } else {
            filteredHosts = hostList
        }
        tableView.reloadData()
    }
    

    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        searchController.dismiss(animated: false, completion: nil)
    }
    
}
