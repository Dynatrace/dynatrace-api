//
//  ProcessGroupTableViewController.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 2/6/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit

class ProcessGroupTableViewController: UITableViewController, UISearchResultsUpdating {
    
    let searchController = UISearchController(searchResultsController: nil)
    var pgList: [String: String] = [:]
    var FilteredPgs: [String: String] = [:]
    
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
        for (entId,pg) in topo.ProcessGroups {
            pgList[entId] = pg.displayName
        }
        FilteredPgs=pgList
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }

    // MARK: - Table view data source

    override func numberOfSections(in tableView: UITableView) -> Int {
        return 1
    }

    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return FilteredPgs.count
    }

    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let keys = Array(FilteredPgs).sorted(by: {$0.1.lowercased() < $1.1.lowercased()})
        let cellIdentifier = "processGroupCell"
        let cell = self.tableView.dequeueReusableCell(withIdentifier: cellIdentifier, for: indexPath) as! ProcessGroupTableViewCell
        let key = keys[indexPath.row].key
        let processGroup = topo.ProcessGroups[key]
        cell.processGroupName.text = processGroup?.displayName ?? ""
        let numPGI=topo.ProcessGroups[key]?.numPGIs ?? 0
        cell.numPGI.text="\(numPGI)"
        cell.entityId=processGroup!.entityId
        
        return cell
    }

    func updateSearchResults(for searchController: UISearchController){
        if let searchText = searchController.searchBar.text {
            if !searchText.isEmpty {
                FilteredPgs = pgList.filter { (key,val) in
                    return val.lowercased().contains(searchText.lowercased())
                }
                
            }
        } else {
            FilteredPgs = pgList
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

    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
    //     if segue.identifier == "processGroupSegue"
    //    {
            if let destVC = segue.destination as? ProcessGroupViewController {
                let cell = sender as? ProcessGroupTableViewCell
                destVC.incomingEntityId=cell!.entityId
            }
    //    }
    }


}
