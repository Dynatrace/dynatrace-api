//
//  ApplicationsTableViewController.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 1/31/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit

class ApplicationsTableViewController: UITableViewController, UISearchResultsUpdating {

    let searchController = UISearchController(searchResultsController: nil)
    var appList: [String: String] = [:]
    var filteredApps: [String: String] = [:]
    
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
        for (entId,app) in topo.Applications {
            appList[entId] = app.displayName
        }
        filteredApps=appList
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
        return filteredApps.count
    }
    
    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let keys = Array(filteredApps).sorted(by: { $0.1.lowercased() < $1.1.lowercased() })
        let cellIdentifier = "applicationCell"
        let cell = self.tableView.dequeueReusableCell(withIdentifier: cellIdentifier, for: indexPath) as! ApplicationTableViewCell
        let key = keys[indexPath.row].key
        cell.applicationName.text = filteredApps[key] ?? ""
        cell.entityId=key
               
        return cell
    }

    func updateSearchResults(for searchController: UISearchController){
        if let searchText = searchController.searchBar.text {
            if !searchText.isEmpty {
                filteredApps = appList.filter { (key,val) in
                    return val.lowercased().contains(searchText.lowercased())
                }
 
            }
        } else {
            filteredApps = appList
        }
        searchController.searchBar.showsCancelButton = false
        tableView.reloadData()
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        searchController.dismiss(animated: false, completion: nil)
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

    // In a storyboard-based application, you will often want to do a little preparation before navigation
     override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        if segue.identifier == "ApplicationSegue"
        {
            if let destVC = segue.destination as? ApplicationViewController {
                let cell = sender as? ApplicationTableViewCell
                destVC.incomingEntityId=cell!.entityId
            }
        }
     }
 

}
