
function plotFromErigonLogEvents(data) {
    let events = data.events;
    let times = [];
    let block_nums = [];
    let block_speeds = [];
    let execution_from = 0;
    let execution_to = 1;
    for (let d of events) {
        if (d.type == "execution") {
            times.push(d.time);
            block_nums.push(parseFloat(d.info.blk_num));
            block_speeds.push(parseFloat(d.info.blk_per_s));
        } else if (d.type == "execution_limits") {
            execution_from = d.info.from;
            execution_to = parseInt(d.info.to);
            //vals.push(5);
        }
    }
    console.log(execution_to);

    let xmin = times[0];
    let xmax = times[times.length - 1];

    let last_date = new Date(times[times.length - 1]);
    let date2 = new Date(times[times.length - 20]);
    let difference = last_date.getTime()-date2.getTime();
    console.log("Difference: " + difference / 1000 + "s.");
    let dif_secs = difference / 1000;


    let last_speed = (block_nums[times.length - 1] - block_nums[times.length - 20]) / dif_secs;
    console.log("Block per sec: " + last_speed);
    console.log(last_speed);

    let block_left = execution_to - block_nums[times.length - 1];
    console.log("Block left: " + block_left);
    let time_left = block_left / last_speed;
    console.log("Time left: " + time_left);

    //todo
    last_date.getTime()
    let new_date = new Date();
    new_date.setSeconds(last_date.getSeconds() + time_left);
    let new_date_str = new_date.toISOString();





    let plotlyData = [
        {
            x: times,
            y: block_nums,
            type: 'scatter',
        },
        {
            x: [xmin, new_date_str],
            y: [execution_to, execution_to],
            type: 'scatter'
        },
        {
            x: [xmin, new_date_str],
            y: [execution_from, execution_from],
            type: 'scatter'
        },
        {
            x: [xmax, new_date_str],
            y: [block_nums[times.length - 1], execution_to],
            type: 'scatter',

        }
    ];
}