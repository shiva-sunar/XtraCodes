//Fetches Inventory details using the PC name 
function printData(url) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url);
    xhr.onload = function () {
        var parser = new DOMParser();
        var doc = parser.parseFromString(xhr.responseText, "text/html");
        var serial = doc.querySelector("body > table > tbody > tr:nth-child(2) > td:nth-child(1)");
        var pcName = doc.querySelector("body > table > tbody > tr:nth-child(2) > td:nth-child(2)");
        var agentID = doc.querySelector("body > table > tbody > tr:nth-child(2) > td:nth-child(3)");
        var assignedDate = doc.querySelector("body > table > tbody > tr:nth-child(2) > td:nth-child(4)");
        var returnedDate = doc.querySelector("body > table > tbody > tr:nth-child(2) > td:nth-child(5)");
        var status = doc.querySelector("body > table > tbody > tr:nth-child(2) > td:nth-child(6)");
        try {
            console.log(pcName.innerHTML, ",", serial.innerHTML, ",", agentID.innerHTML, ",", assignedDate.innerHTML, ",", returnedDate.innerHTML, ",", status.innerHTML);
        } catch (error) {
            console.log(error);
        }
        // Use the selected element
    };
    xhr.send();
}
const pcList = [xxx];
console.log("PC Name", ",", "Serial", ",", "Agent ID", ",", "Assigned Date", ",", "Returned Date", ",", "Status");
for (let i = 0; i < pcList.length; i++) {
    var pcSN = pcList[i];
    var url = "http://xxx/inventory/researchInventory.php?serialnumber=&agentId=&pcname=" + pcSN + "&validate=Search";
    // console.log(url);
    printData(url);
}
