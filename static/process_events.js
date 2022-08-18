function getDateDifferenceInSecs(date1, date2) {
    return (date1.getTime() - date2.getTime()) / 1000;
}


function plotFromErigonLogEvents(data, sizes) {
    let events = data.events;
    let times = [];
    let block_nums = [];
    let block_speeds = [];
    let execution_from = 0;
    let execution_to = 1;
    for (let d of events) {
        if (d.type == "execution") {
            times.push(new Date(d.time));
            block_nums.push(parseFloat(d.info.blk_num));
            block_speeds.push(parseFloat(d.info.blk_per_s));
        } else if (d.type == "execution_limits") {
            execution_from = d.info.from;
            execution_to = parseInt(d.info.to);
            //vals.push(5);
        }
    }
    console.log(execution_to);

    let sizes_times = []
    let sizes_values = []
    console.log(sizes);
    for (let dt in sizes) {
        sizes_times.push(dt);
        sizes_values.push(sizes[dt]["erigon_data_size"]);

    }


    if (times.length > 10) {
        let xmin = times[0];
        let xmax = times[times.length - 1];

        let last_date = times[times.length - 1];

        const COMPARE_EVENTS_BEFORE = Math.min(50, times.length - 1);
        let date2 = times[times.length - COMPARE_EVENTS_BEFORE];
        let dif_secs = getDateDifferenceInSecs(last_date, date2);


        let last_speed = (block_nums[times.length - 1] - block_nums[times.length - COMPARE_EVENTS_BEFORE]) / dif_secs;
        console.log("Block per sec: " + last_speed);
        console.log(last_speed);

        let block_left = execution_to - block_nums[times.length - 1];
        console.log("Block left: " + block_left);
        let time_left = block_left / last_speed;
        console.log("Time left: " + time_left);

        //todo
        last_date.getTime()
        let new_date = new Date();

        //new_date.setUTCSeconds(last_date.getUTCSeconds());
        new_date.setTime(last_date.getTime() + time_left * 1000);

        let plotlyData = [
            {
                x: times,
                y: block_nums,
                type: 'scatter',
            },
            {
                x: [xmin, new_date],
                y: [execution_to, execution_to],
                type: 'scatter'
            },
            {
                x: [xmin, new_date],
                y: [execution_from, execution_from],
                type: 'scatter'
            },
            {
                x: [xmax, new_date],
                y: [block_nums[times.length - 1], execution_to],
                type: 'scatter',

            },
            {
                x: sizes_times,
                y: sizes_values,
                type: 'scatter',
                yaxis: 'y2'
            }
        ];
        return {
            "plotlyData": plotlyData,
            "lastSpeed": last_speed,
            "estimatedCompletion": new_date,
            "lastDate": last_date,
        };
    }

    return [];








}