var xhr = new XMLHttpRequest();
xhr.open("GET", "https://us-central1-koverholt-apps-304316.cloudfunctions.net/texas-exes-events");
xhr.setRequestHeader("Content-Type", "application/json");
xhr.send();

xhr.onload = function () {
  var obj = JSON.parse(this.response);
  var event_counts = obj["event_counts"];
  var fetch_date = obj["fetch_date"];

  var app = new Vue({
    el: '#app',
    data: {
      event_counts: event_counts,
      fetch_date: fetch_date,
    }
  })
};
