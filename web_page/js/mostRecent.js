
async function mostRecent(){

 // Assemble the URL from the text boxes (maybe I should move to a POST method, I'm not sure)
 let url='/vso-health-report-most-recent-status';
 let sepChar='?';


 numBox=0;
 if (document.getElementById('providerBox').value.length > 1){
  url += sepChar + 'Provider=' + document.getElementById('providerBox').value;
  numBox++;
  sepChar='&';
 }

 if (document.getElementById('sourceBox').value.length > 1){
  url += sepChar + 'Source=' + document.getElementById('sourceBox').value;
  sepChar='&';
  numBox++;
 }

 if (document.getElementById('instrumentBox').value.length > 1){
  url += sepChar + 'Instrument=' + document.getElementById('instrumentBox').value;
  sepChar='&';
  numBox++;
 }

 if (numBox < 3){
    alert("All three of Provider, Source, Instrument must be specified");
    return;
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

 document.getElementById('resultPara').innerHTML = 'Most recent status is ' +
          resultsObj.result.Status + " at time " + resultsObj.result.Timestring +
          " for provider <b>" + resultsObj.result.Provider +
          "</b> Source <b>" + resultsObj.result.Source +
          "</b> Instrument <b>" + resultsObj.result.Instrument + "</b>";

 return;

}

