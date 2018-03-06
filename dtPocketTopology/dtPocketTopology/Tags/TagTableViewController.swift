//
//  TagTableViewController.swift
//  dtPocketTopology
//
//  Created by Hocker, Lucas on 3/2/18.
//  Copyright © 2018 Hocker, Lucas. All rights reserved.
//

import UIKit

class TagTableViewController: UITableViewController, UISearchResultsUpdating, UISearchBarDelegate {

    let searchController = UISearchController(searchResultsController: nil)
    var filteredEntIds:   [String] = []
    var entIdList:        [String] = []
    var incomingTag:      String = ""
    
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
        
        entIdList =  topo.Tags[incomingTag] ?? Array()
        filteredEntIds=entIdList
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
        return filteredEntIds.count
    }
    
    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let keys = filteredEntIds.sorted(by: <)
        let cellIdentifier = "tagCell"
        let cell = self.tableView.dequeueReusableCell(withIdentifier: cellIdentifier, for: indexPath) as! TagTableViewCell
        let key = keys[indexPath.row]
        cell.entId.text=key
        cell.entType.text=updateEntTypes(entId: cell.entId.text ?? "")
        switch(cell.entType.text){
        case "HOST"?:
            let name=topo.Hosts[cell.entId.text!]?.displayName
            cell.hostButton.setTitle(name, for: .normal)
            cell.hostButton.isHidden=false
            cell.hostButton.entityId=key
        case "APPLICATION"?:
            let name=topo.Applications[cell.entId.text!]?.displayName
            cell.applicationButton.setTitle(name, for: .normal)
            cell.applicationButton.isHidden=false
            cell.applicationButton.entityId=key
        case "SERVICE"?:
            let name=topo.Services[cell.entId.text!]?.displayName
            cell.serviceButton.setTitle(name, for: .normal)
            cell.serviceButton.isHidden=false
            cell.serviceButton.entityId=key
        case "PROCESS_GROUP_INSTANCE"?:
            let name=topo.Processes[cell.entId.text!]?.displayName
            cell.processButton.setTitle(name, for: .normal)
            cell.processButton.isHidden=false
            cell.processButton.entityId=key
        case "PROCESS_GROUP"?:
            let name=topo.ProcessGroups[cell.entId.text!]?.displayName
            cell.processGroupButton.setTitle(name, for: .normal)
            cell.processGroupButton.isHidden=false
            cell.processGroupButton.entityId=key
        default:
            cell.displayName.text="UnknownType"
            cell.displayName.isHidden=false
        }
       
        return cell
    }

    func updateEntTypes(entId: String) -> String
    {
        //let entId = keys[indexPath.row].key
        let dash=entId.index(of: "-") ?? entId.endIndex
        let entType=entId[..<dash]
        return String(entType)
        
    }
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
        switch(segue.identifier)
        {
        case "hostSegue"?:
            if let destVC = segue.destination as? HostViewController {
                let button = sender as? TagUIButton
                destVC.incomingEntityId=button!.entityId
             }
        case "serviceSegue"?:
            if let destVC = segue.destination as? ServiceViewController {
                let button = sender as? TagUIButton
                destVC.incomingEntityId=button!.entityId
            }
        case "applicationSegue"?:
            if let destVC = segue.destination as? ApplicationViewController {
                let button = sender as? TagUIButton
                destVC.incomingEntityId=button!.entityId
            }
        case "processSegue"?:
            if let destVC = segue.destination as? ProcessViewController {
                let button = sender as? TagUIButton
                destVC.incomingEntityId=button!.entityId
            }
        case "processGroupSegue"?:
            if let destVC = segue.destination as? ProcessGroupViewController {
                let button = sender as? TagUIButton
                destVC.incomingEntityId=button!.entityId
            }
        default:
            return
        }
    }
    
    func updateSearchResults(for searchController: UISearchController) {
        if let searchText = searchController.searchBar.text {
            if !searchText.isEmpty {
                filteredEntIds = entIdList.filter { key in
                    return key.lowercased().contains(searchText.lowercased())
                }
                
            }
        } else {
            filteredEntIds = entIdList
        }
        tableView.reloadData()
    }
    
    
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        searchController.dismiss(animated: false, completion: nil)
    }

}
