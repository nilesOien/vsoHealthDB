

async function getTime(){

 let url='/vso-health-report-max-time';
 let response = await fetch(url);

 if (response.status != 200) {
   alert(response.statusText);
   return;
 }

 // The returned JSON should look something like this :
 // {
 //  "statusMessage": "Success",
 //  "statusCode": 0,
 //  "maxTime": "20260522_130015"
 //  "minTime": "20220125_130015"
 // }
 let responseText = await response.text();

 try {
   var maxTimeObj = JSON.parse(responseText);
 } catch (error) {
   alert("Error parsing max time JSON:", error.message);
   return;
 }

 // If there was a server side error, percolate it up to the user
 // so they can send an email.
 if (maxTimeObj.statusCode != 0){
   alert(maxTimeObj.statusMessage + " Status code : " + maxTimeObj.statusCode);
   return;
 }

 document.getElementById('firstPara').innerHTML = "The latest health report run is timestamped " + maxTimeObj.maxTime +
                                                  " and the first run is timestamped " + maxTimeObj.minTime;

 return;
}

