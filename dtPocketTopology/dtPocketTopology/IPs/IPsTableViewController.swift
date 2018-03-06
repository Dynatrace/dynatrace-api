//
//  IPsTableViewController.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 3/1/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit

class IPsTableViewController: UITableViewController, UISearchResultsUpdating, UISearchBarDelegate {
    let searchController = UISearchController(searchResultsController: nil)
    var ipList: [String: String] = [:]
    var filteredIPs: [String: String] = [:]
    override func viewDidLoad() {
        super.viewDidLoad()

        // Uncomment the following line to preserve selection between presentations
        // self.clearsSelectionOnViewWillAppear = false

        // Uncomment the following line to display an Edit button in the navigation bar for this view controller.
        // self.navigationItem.rightBarButtonItem = self.editButtonItem
        
        searchController.searchResultsUpdater = self
        tableView.tableHeaderView = searchController.searchBar
        searchController.hidesNavigationBarDuringPresentation = false
        searchController.dimsBackgroundDuringPresentation = false
        
        ipList=topo.IPs
        filteredIPs=ipList
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }

    // MARK: - Table view data source

    override func numberOfSections(in tableView: UITableView) -> Int {
        return 1
    }
    
    override func tableView(_ tableView: UITableView, numberOfRowsInSection: Int) -> Int {
        return filteredIPs.count
    }
    
    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let keys = filteredIPs.sorted(by: {
            return $0.0 < $1.0
        })
        let cellIdentifier = "ipCell"
        let cell = self.tableView.dequeueReusableCell(withIdentifier: cellIdentifier, for: indexPath) as! IPTableViewCell
        let key = keys[indexPath.row].key
        cell.ip.text=key
        //cell.tagLabel.sizeToFit()
        let entId = topo.IPs[key]
        cell.hostname.text=topo.Hosts[entId!]?.displayName ?? ""
        cell.entityId=entId!
        return cell
    }

    /*
    // Override to support conditional editing of the table view.
    override func tableView(_ tableView: UITableView, canEditRowAt indexPath: IndexPath) -> Bool {
        // Return false if you do not want the specified item to be editable.
        return true
    }
    */

    /*
    // Override to support editing the table view.
    override func tableView(_ tableView: UITableView, commit editingStyle: UITableViewCellEditingStyle, forRowAt indexPath: IndexPath) {
        if editingStyle == .delete {
            // Delete the row from the data source
            tableView.deleteRows(at: [indexPath], with: .fade)
        } else if editingStyle == .insert {
            // Create a new instance of the appropriate class, insert it into the array, and add a new row to the table view
        }    
    }
    */

    /*
    // Override to support rearranging the table view.
    override func tableView(_ tableView: UITableView, moveRowAt fromIndexPath: IndexPath, to: IndexPath) {

    }
    */

    /*
    // Override to support conditional rearranging of the table view.
    override func tableView(_ tableView: UITableView, canMoveRowAt indexPath: IndexPath) -> Bool {
        // Return false if you do not want the item to be re-orderable.
        return true
    }
    */


    // MARK: - Navigation

    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        if segue.identifier == "ipSegue"
        {
            if let destVC = segue.destination as? HostViewController {
             let cell = sender as? IPTableViewCell
                destVC.incomingEntityId=cell!.entityId
             }
        }
    }
    
    func updateSearchResults(for searchController: UISearchController) {
        if let searchText = searchController.searchBar.text {
            if !searchText.isEmpty {
                filteredIPs = ipList.filter { (key,val) in
                    return key.lowercased().contains(searchText.lowercased())
                }
                
            }
        } else {
            filteredIPs = ipList
        }
        tableView.reloadData()
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        searchController.dismiss(animated: false, completion: nil)
    }


}
