var markerCluster;
var markers = [];
var circlesMarker = [];
var circlesMeasurement = [];
var map;
var circleShowed = false;
var thresholdEmptyCircle=6371;
var center =  new google.maps.LatLng(48.6908333333, 9.14055555556);
var markerInTheCluster;
var data;
var mplaneCapability, mplaneSpecification, mplaneResult;
var dateMeasurement,functionFinished;

//trick for wait until the data are downloaded
function waitForLoadingData() {
    if (typeof data === "undefined") {
        setTimeout(waitForLoadingData, 100);
    } else {
        reloadMarkers()
    }
}

function initialize() {
    //****mPlane Message****\\
    mplaneCapability = 'mPlane Capability:\n{\"capability\": \"anycast-geolocation\",\n  \"version\": 1,\n  \"registry\": \"http://ict-mplane.eu/registry/core\",\n  \"when\": \"2015-03-25 13:05:50 ... future\",\n  \"parameters\": {\n"source.ip4\": \"127.0.0.1\",\n                 \"destination.ip4\": \"*\"},\n  \"results\": [\"anycast\",\n              \"anycastGeolocation\"]}'
    myTextArea = document.getElementById('mplaneMessage');
    myTextArea.innerHTML = mplaneCapability;
    //****mPlane Message****\\

    //****map option****\\
    map = new google.maps.Map(document.getElementById('map'), {
    zoom: 2,    
    minZoom: 2,
    center: center,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    zoomControlOptions: {
      style: google.maps.ZoomControlStyle.SMALL
    }
    });
    markerCluster = new MarkerClusterer(map, [], {
        minimumClusterSize: '6'
    });
    //****map option****\\

    manageToggle(); //initialise all the toggle variable
}

//real time measurement
function measure(){
     dateMeasurement="now";
     mplaneSpecification= '\n\nmPlane Specification:\n{\"capability\": \"anycast-geolocation\",\n  \"version\": 1,\n  \"registry\": \"http://ict-mplane.eu/registry/core\",\n  \"when\": \"now\",\n  \"parameters\": {\n"source.ip4\": \"127.0.0.1\",\n                 \"destination.ip4\": \"'+ document.getElementById("suggestBox").value.split("\t")[0]+'\"},\   \"results\": [\"anycast\",\n              \"anycastGeolocation\"]}'
     myTextArea.innerHTML+= mplaneSpecification;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
          document.getElementById("suggestBox").value=xhttp.responseText;
          loadLocation();
        }
    }
    xhttp.open("GET", "http://127.0.0.1/?ip="+document.getElementById("suggestBox").value.split("\t")[0], true);
    xhttp.send();
    dateMeasurement=(new Date().toJSON().slice(0,10))+" "+(new Date().toJSON().slice(11,19))
}

//****mPlane Message****\\
//control for show only valid IP
function checkInput(){
    if( document.getElementById("suggestBox").value.split("\t")[0].split(".").length==4)
        return true;
}

function setSpecification(){
    if( checkInput()){
         dateMeasurement="2015-03-25 13:05:50"
         mplaneSpecification= '\n\nmPlane Specification:\n{\"specification\": \"anycast-geolocation\",\n  \"version\": 1,\n  \"registry\": \"http://ict-mplane.eu/registry/core\",\n   \"token\": \"ea839b56bc3f6004e95d780d7a64d899\",\n   \"when\": \"2015-03-25 13:05:50\",\n  \"parameters\": {\n"source.ip4\": \"127.0.0.1\",\n                 \"destination.ip4\": \"'+ document.getElementById("suggestBox").value.split("\t")[0]+'\"},\n  \"results\": [\"anycast\",\n              \"anycastGeolocation\"]}'
    myTextArea.innerHTML+= mplaneSpecification;
    }
}
//****mPlane Message****\\

function loadLocation() {
    functionFinished=false

    //reset variable
    /*
    //document.getElementById('reset10Ranking').selected = true;
    //document.getElementById('reset10Size').selected = true;
    //document.getElementById('resetPublicInfo').selected = true;
    //document.getElementById('resetGroundTruth').selected = true;
    */

   //document.getElementById('resetSelector').selected = true;
    document.getElementById('numberInstanceGT').innerHTML = "";
    data = undefined
    //resetMap
    //map.setCenter(center);
    //map.setZoom(2);
//TODO: try to clean
    circleShowed = true
    showCircles();

//-------------------------------
    circlesMarker = new Array()
    circlesMeasurement = []
//it wait 500ms, for read the right input(otherwise it will be empty the input)
    setTimeout(function() {
        var s = document.createElement('script');
        s.setAttribute('src', "data/anycastJson/" + document.getElementById("suggestBox").value.split("\t")[0]);
        document.body.appendChild(s);
    }, 500);

    waitForLoadingData()

//draw graphs after loaded the location
    drawLinesChart();
    drawPie('platformPie', dataPlatforms);
    drawPie('countryPie', dataCountry);

}

function reloadMarkers() {
    circlesMarker = new Array()
    anycastResult="True"
    if (data.count<2)
        anycastResult="False"

    mplaneResult= '\n\nmPlane Result:\n{\"result\": \"anycast-geolocation\",\n  \"version\": 1,\n  \"registry\": \"http://ict-mplane.eu/registry/core\",\n   \"token": "ea839b56bc3f6004e95d780d7a64d899\",   \n\"when\": \"'+dateMeasurement+'\",\n  \"parameters\": {\n"source.ip4\": \"127.0.0.1\",\n                 \"destination.ip4\": \"'+ document.getElementById("suggestBox").value.split("\t")[0].split("-")[0]+'\"},\n  \"results\": [\"anycast\",\n              \"anycastGeolocation\"]\n   \"resultvalues\": [\"'+anycastResult+'\", \"'+JSON.stringify(data)+'\"]}'
        myTextArea.innerHTML+= mplaneResult;

    document.getElementById('numberInstance').innerHTML = "Number of instances: " + data.count
    document.getElementById('hitToggle').checked=false;
    showMarkersHit()

    // Reset the markers array
    markers = [];
    heatData=[];

    //Read the new markers
    for (var i = 0; i < data.count; i++) {
        var markerData = data.instances[i].marker;
//------------HEATMAPTOFIX---------------
        var lat=parseFloat(markerData.latitude)+(Math.random() * (0.0250) + 0.14200);
        var lng=parseFloat(markerData.longitude)+(Math.random() * (0.0250) + 0.14200); //TODO: change
        //alert(markerData.longitude.toString()+"  "+lng.toString()+"  "+(Math.random() * (0.0150) + 2.54200))
        heatData[i] = new google.maps.LatLng(lat,lng);
//------------HEATMAPTOFIX---------------
        
        var latLng = new google.maps.LatLng(lat,lng);

        var marker = new google.maps.Marker({
            position: latLng,
            title: markerData.id+"<br />City:"+markerData.city+"<br />Country:"+markerData.code_country,
            icon: "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=H|00FF00|000000"
        });
 
        var circleData = data.instances[i].circle;
        var drawCircle = new google.maps.Circle({
            center: new google.maps.LatLng(circleData.latitude, circleData.longitude),
            radius: circleData.radius * 1000, // metres
            strokeColor: '#FF0000',
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: '#FF0000',
            fillOpacity: 0.35,
        });

        google.maps.event.addListener(marker, 'click', function() {
            var infowindow = new google.maps.InfoWindow({
        content: "<p>" + "Iata: " + this.getTitle() + "<br />Latitude: " + this.getPosition().lat().toFixed(5) + "<br />Longitude: " + this.getPosition().lng().toFixed(5)
            });
            infowindow.open(map, this);
        });
        <!-- end draw circle-->
        markers.push(marker);
        circlesMarker.push(drawCircle)

        }

    //read the all the empty circle
    
    for (var i = 0; i < data.countAllCircles; i++) {
        var circleData = data.allCircles[i]; 
        if(parseFloat(circleData.radius)<thresholdEmptyCircle){
        var drawCircle = new google.maps.Circle({
            center: new google.maps.LatLng(circleData.latitude, circleData.longitude),
            radius: circleData.radius * 1000, // metres
            strokeColor: '#FF0000',
            strokeOpacity: 0.2,
            strokeWeight: 2,
            fillColor: '#FF0000',
            fillOpacity: 0.00,
        });
        circlesMarker.push(drawCircle)
        }
        }

    manageToggle('initialize')

    //Add the new marker to the cluster
    if(document.getElementById('cluster').checked)
        {markerCluster.addMarkers(markers) }//it should check before}
    functionFinished=true
}
  
function updateEmptyCircle(threshold){
    document.querySelector('#volume').value = threshold+" km";
    thresholdEmptyCircle=threshold;
}
function updateEmptyCircle2(threshold){
    document.querySelector('#volume').value = threshold+" km";
    thresholdEmptyCircle=threshold;
    loadLocation()
    waitForLoadLocation()
}
//trick for wait until the data are downloaded
function waitForLoadLocation() {
    if (functionFinished == false) {
        setTimeout(waitForLoadLocation, 100);
    } else {
        checkToggle('circlesToggle')
    }
}

google.maps.event.addDomListener(window, 'load', initialize);
