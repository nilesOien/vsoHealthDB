
// Small function to get a status description.
// You pass in an integer status, you get a status description string back.
function getStatusDescription(status){

 if (status == 0){ return "The test passed"; }
 if (status == 1){ return "The test passed on a known query"; }
 if (status == 2){ return "The test was skipped"; }
 if (status == 8){ return "The test failed on data download"; }
 if (status == 9){ return "The test failed due to no response"; }
 return "Unknown status";
}

// Function that clears the tables
function clearTable(){
 document.getElementById('keyTable').innerHTML = "";
 document.getElementById('resultsTable').innerHTML = "";
 document.getElementById('footerPara').innerHTML="";
 return;
}



// Function that populates the key table.
function populateKeyTable(){

  let h = "<tr>";
           h+="<td><b>Icon</b></td><td><b>Meaning</b></td><td><b>Status code</b></td>";
           h+="</tr>";
           h+="<tr>";
           h+="<td><img src=\"statusIconFactory/status0.jpg\"></td>";
           h+="<td><b>Test passed</b></td>";
           h+="<td><b>0</b></td>";
           h+="</tr>";
           h+="<tr>";
           h+="<td><img src=\"statusIconFactory/status1.jpg\"></td>";
           h+="<td><b>Test passed on known request</b></td>";
           h+="<td><b>1</b></td>";
           h+="</tr>";
           h+="<tr>";
           h+="<td><img src=\"statusIconFactory/status2.jpg\"></td>";
           h+="<td><b>Skipped, no test performed</b></td>";
           h+="<td><b>2</b></td>";
           h+="</tr>";
           h+="<tr>";
           h+="<td><img src=\"statusIconFactory/status8.jpg\"></td>";
           h+="<td><b>Test failed on data download</b></td>";
           h+="<td><b>8</b></td>";
           h+="</tr>";
           h+="<tr>";
           h+="<td><img src=\"statusIconFactory/status9.jpg\"></td>";
           h+="<td><b>Test failed with no response</b></td>";
           h+="<td><b>9</b></td>";
           h+="</tr>";

 document.getElementById('keyTable').innerHTML = h;

 return;

}


async function populateTable(){

 clearTable();

 // Assemble the URL from the text boxes (maybe I should move to a POST method, I'm not sure)
 let url='/vso-health-report-data';
 let sepChar='?';
 if (document.getElementById('minTimeBox').value.length > 14){
  url += sepChar + 'minTime=' + document.getElementById('minTimeBox').value;
  sepChar='&';
 }

 if (document.getElementById('maxTimeBox').value.length > 14){
  url += sepChar + 'maxTime=' + document.getElementById('maxTimeBox').value;
  sepChar='&';
 }

 if (document.getElementById('providerBox').value.length > 1){
  url += sepChar + 'providerCSV=' + document.getElementById('providerBox').value;
  sepChar='&';
 }

 if (document.getElementById('sourceBox').value.length > 1){
  url += sepChar + 'sourceCSV=' + document.getElementById('sourceBox').value;
  sepChar='&';
 }

 if (document.getElementById('instrumentsBox').value.length > 1){
  url += sepChar + 'instrumentCSV=' + document.getElementById('instrumentsBox').value;
  sepChar='&';
 }

 if (document.getElementById('statusBox').value.length > 0){
  url += sepChar + 'statusCSV=' + document.getElementById('statusBox').value;
  sepChar='&';
 }


 console.log(url)


 let response = await fetch(url);

 if (response.status != 200) {
   alert(response.statusText);
   return;
 }

 let responseText = await response.text();

 try {
   var statusMatrixObj = JSON.parse(responseText);
 } catch (error) {
   alert("Error parsing status matrix JSON:", error.message);
   return;
 }

 // If there was a server side error, percolate it up to the user
 // so they can send an email.
 if (statusMatrixObj.statusCode != 0){
   alert(statusMatrixObj.statusMessage + " Status code : " + statusMatrixObj.statusCode);
   return;
 }

 // Put a header row on the table that lists times.
 let h="<tr><td><b>Provider</b></td><td><b>Source</b></td><td><b>Instrument</b></td>";
 for (const [tmstring, providerObj] of Object.entries(statusMatrixObj.results)) {
  h+="<td><b>" + tmstring.substring(0,8) + "<br>" + tmstring.substring(9,15) + "</b></td>";
 }
 h += "</tr>";

 let numStatusReported=0;
 // Then list the provider,source,instruments in subsequent rows.
 for (const [num, psi_dict] of Object.entries(statusMatrixObj.psi_list)) {
  // console.log(psi_dict)
  h += "<tr><td>" + psi_dict['Provider'] + "</td><td>" + psi_dict['Source'] + "</td><td>" + psi_dict['Instrument'] + "</td>";
  for (const [tmstring, providerObj] of Object.entries(statusMatrixObj.results)) {

   // Learned the hard way that I need to check incrementally at
   // different levels of the nested dictionary to see if everything is defined.
   if (statusMatrixObj.results[tmstring][psi_dict['Provider']] === undefined){
    h+="<td></td>";
    continue;
   }

   if (statusMatrixObj.results[tmstring][psi_dict['Provider']][psi_dict['Source']] === undefined){
    h+="<td></td>";
    continue;
   }

   if (statusMatrixObj.results[tmstring][psi_dict['Provider']][psi_dict['Source']][psi_dict['Instrument']] === undefined){
    h+="<td></td>";
    continue;
   }

   let status=statusMatrixObj.results[tmstring][psi_dict['Provider']][psi_dict['Source']][psi_dict['Instrument']];
   if (status === undefined){
    h += "<td></td>";
   } else {
    let statusStr = getStatusDescription(status);
    let hoverStr = statusStr + 
           " for provider " + psi_dict['Provider'] + ", source " + psi_dict['Source'] + ", instrument " + psi_dict['Instrument'];
    hoverStr += " at " + tmstring;
    h+="<td><img src=\"statusIconFactory/status" + status + ".jpg\" title=\"" + hoverStr + "\"></td>";
    numStatusReported++;
   }
  }
  h += "</tr>";
 }

 document.getElementById('resultsTable').innerHTML = h;
 document.getElementById('footerPara').innerHTML= numStatusReported + " matching status reports found";

 populateKeyTable();

 return;
}

