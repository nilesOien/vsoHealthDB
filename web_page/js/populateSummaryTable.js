
function clearTable(){

  document.getElementById('resultsTable').innerHTML = "";
  document.getElementById('skippedTable').innerHTML = "";
  document.getElementById('skippedPara').innerHTML = "";

  return;

}

async function populateSummaryTable(){

 clearTable();

 // Assemble the URL from the text boxes (maybe I should move to a POST method, I'm not sure)
 let url='/vso-health-report-summary';
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

 if (document.getElementById('orderByPG').checked){
  url += sepChar + 'orderBy=percentGood';
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
   var resultsObj = JSON.parse(responseText);
 } catch (error) {
   alert("Error parsing status matrix JSON:", error.message);
   return;
 }

 // If there was a server side error, percolate it up to the user
 // so they can send an email.
 if (resultsObj.statusCode != 0){
   alert(resultsObj.statusMessage + " Status code : " + resultsObj.statusCode);
   return;
 }

 // Put a header row on the table that lists times.
 let h="<tr><td><b>Provider</b></td><td><b>Source</b></td><td><b>Instrument</b></td>";
 h += "<td><b>Pass count</b></td><td><b>Fail count</b></td><td><b>Percent good</b></td>";
 h += "</tr>";

 for (const item of resultsObj.results){
  h += "<tr><td>" + item['Provider'] + "</td><td>" + item['Source'] + "</td><td>" + item['Instrument']  + "</td>";
  h += "<td>"     + item['numGood'] +  "</td><td>" + item['numBad'] + "</td><td>" + item['percentGood'] + "</td></tr>";
 }

 document.getElementById('resultsTable').innerHTML = h;

 if (resultsObj.skipped.length == 0){
  return;
 }


 document.getElementById('skippedPara').innerHTML = resultsObj.skipped.length + " instruments were skipped (never tested in this time range) :";
 h="<tr><td><b>Provider</b></td><td><b>Source</b></td><td><b>Instrument</b></td></tr>";
 for (const item of resultsObj.skipped){
  h += "<tr><td>" + item['Provider'] + "</td><td>" + item['Source'] + "</td><td>" + item['Instrument']  + "</td></tr>";
 }

 document.getElementById('skippedTable').innerHTML = h;

 return;

}

