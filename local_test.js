var fs = require('fs');

// file is included here:
eval(fs.readFileSync('process_events.js')+'')

let rawdata = fs.readFileSync('test.json');
let data = JSON.parse(rawdata);

plotFromErigonLogEvents(data);
console.log("test");
