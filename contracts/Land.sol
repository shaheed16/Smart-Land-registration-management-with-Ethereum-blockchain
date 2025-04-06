// SPDX-License-Identifier: MIT
pragma solidity >= 0.4.0 <= 0.9.0;

contract Land {
    string public user_details;
    string public land_details;
    string public history;
    string public purchase;

    function setUserDetails(string memory ud) public {
        user_details = ud;	
    }

    function getUserDetails() public view returns (string memory) {
        return user_details;
    }

    function setLandDetails(string memory pd) public {
        land_details = pd;	
    }

    function getLandDetails() public view returns (string memory) {
        return land_details;
    }


    function sethistory(string memory p) public {
        history = p;	
    }

    function gethistory() public view returns (string memory) {
        return history;
    }

    function setpurchase(string memory pp) public {
        purchase = pp;	
    }

    function getpurchase() public view returns (string memory) {
        return purchase;
    }


    constructor() public {
    user_details = "";
	land_details = "";
    history = "";
    purchase= "";
    }
}