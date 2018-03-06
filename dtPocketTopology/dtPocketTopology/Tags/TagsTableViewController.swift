//
//  TagsTableViewController.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 3/1/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit

class TagsTableViewController: UITableViewController, UISearchResultsUpdating, UISearchBarDelegate {

    let searchController = UISearchController(searchResultsController: nil)
    var filteredTags:   [String : Int] = [:]
    var tagList:        [String : Int] = [:]
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

        for tag in topo.Tags {
            tagList[tag.key]=tag.value.count
        }
        filteredTags=tagList
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
        return filteredTags.count
    }
    
    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let keys = filteredTags.sorted(by: {
            if $0.1 == $1.1 {
                return $0.0.lowercased() < $1.0.lowercased()
            }
            return $0.1 > $1.1
        })
        let cellIdentifier = "tagsCell"
        let cell = self.tableView.dequeueReusableCell(withIdentifier: cellIdentifier, for: indexPath) as! TagsTableViewCell
        let key = keys[indexPath.row].key
        cell.tagLabel.text=key
        //cell.tagLabel.sizeToFit()
        cell.numTags.text="\(topo.Tags[key]?.count ?? 0)"
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

    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        if segue.identifier == "tagSegue"
        {
            if let destVC = segue.destination as? TagTableViewController {
                let cell = sender as? TagsTableViewCell
                destVC.incomingTag=cell!.tagLabel.text!
            }
        }
    }
    
    func updateSearchResults(for searchController: UISearchController) {
        if let searchText = searchController.searchBar.text {
            if !searchText.isEmpty {
                filteredTags = tagList.filter { (key,val) in
                    return key.lowercased().contains(searchText.lowercased())
                }
                
            }
        } else {
            filteredTags = tagList
        }
        tableView.reloadData()
    }
    
    
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        searchController.dismiss(animated: false, completion: nil)
    }

}
