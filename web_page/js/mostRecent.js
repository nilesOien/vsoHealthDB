
async function mostRecent(){

 let payload={Provider:document.getElementById('providerBox').value,Source:document.getElementById('sourceBox').value,Instrument:document.getElementById('instrumentBox').value};

 let response = await fetch('/vso-health-report-most-recent-status',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});

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

 document.getElementById('resultPara').innerHTML = 'Most recent status is ' +
          resultsObj.result.Status + " at time " + resultsObj.result.Timestring +
          " for provider <b>" + resultsObj.result.Provider +
          "</b> Source <b>" + resultsObj.result.Source +
          "</b> Instrument <b>" + resultsObj.result.Instrument + "</b>";

 return;

}

