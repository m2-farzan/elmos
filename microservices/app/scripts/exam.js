function dayToFullDate(day) {
    const cumsum = (sum => value => sum += value)(0);
    monthDays = [31,31,31,31,31,31,30,30,30,30,30,30];
    monthDaysCumsum = monthDays.map(cumsum);
    month = monthDaysCumsum.findIndex(x => (day <= x));
    monthNames = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'];
    if (month == 0)
        dayOfMonth = day;
    else
        dayOfMonth = day - monthDaysCumsum[month-1];
    return [dayOfMonth, monthNames[month]];
}

function getDisplayRange(exams) {
    if (exams.length == 0)
        return [1, 15];
    days = exams.map(e => e.exam_day).filter(x => x > 0);
    d0 = Math.min.apply(null, days);
    d1 = Math.max.apply(null, days);
    if (d1 - d0 < 15)
        d1 = d0 + 15;
    return [d0, d1];
}

function getExamTable(w, h, exams) {
    var firstDay = getDisplayRange(exams)[0];
    var lastDay = getDisplayRange(exams)[1];
    svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", w);
    svg.setAttribute("height", h);
    
    var n_rows = 7;
    var n_cols = lastDay - firstDay + 2;

    // vlines
    for(i = 1; i < n_cols; i++) {
        line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", i * w / n_cols);
        line.setAttribute("y1", 0);
        line.setAttribute("x2", i * w / n_cols);
        line.setAttribute("y2", h);
        line.setAttribute("style", "stroke:#fff");
        svg.append(line);
    }
    
    // hlines
    for(i = 1; i < n_rows; i++) {
        line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", 0);
        line.setAttribute("y1", i * h / n_rows);
        line.setAttribute("x2", w);
        line.setAttribute("y2", i * h / n_rows);
        line.setAttribute("style", "stroke:#fff");
        svg.append(line);
    }
    
    // day texts
    for(i = 0; i <= lastDay - firstDay; i++) {
        text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        var x = w - (i+1.5) * w / n_cols;
        text.setAttribute("x", x);
        text.setAttribute("y", h/n_rows/2);
        text.setAttribute("dominant-baseline", "middle");
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("style", "fill:white");

        day = firstDay + i;
        dayOfMonth = dayToFullDate(day)[0];
        dayOfMonth_FA = (''+dayOfMonth).replace(/./g, x => String.fromCharCode(x.charCodeAt(0)+1728));
        
        text.innerHTML = dayOfMonth_FA;
        
        svg.append(text);
        
        if (dayOfMonth == 1 || i == 0) {
            // month break
            newMonthText = document.createElementNS("http://www.w3.org/2000/svg", "text");
            newMonthText.setAttribute("x", w - (i+1) * w / n_cols -5);
            newMonthText.setAttribute("y", 0);
            newMonthText.setAttribute("dominant-baseline", "hanging");
            newMonthText.setAttribute("text-anchor", "start");
            newMonthText.setAttribute("style", "fill:white");
            newMonthText.innerHTML = dayToFullDate(day)[1];
            svg.append(newMonthText);
        }
    }

    // day texts
    rowLabels = ['', '۸-۱۰', '۱۰-۱۲', '۱۲-۱۴', '۱۴-۱۶', '۱۶-۱۸', '۱۸-۲۰'];
    for(i = 0; i < n_rows; i++) {
        text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        var y = (i+0.5) * h / n_rows;
        text.setAttribute("x", w - w/n_cols/2);
        text.setAttribute("y", y);
        text.setAttribute("dominant-baseline", "middle");
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("style", "fill:white");

        text.innerHTML = rowLabels[i];
        
        svg.append(text);
    }
    
    for(i = 0; i < exams.length; i++) {
        var x = w - (exams[i].exam_day - firstDay + 2) * w / (n_cols);
        var y = ((exams[i].exam_time - 8) / 2 + 1) * h / (n_rows);

        var div = document.createElement("div");
        div.setAttribute("class", "unit-item item-normal");
        div.setAttribute("style", "width: 100%; height: 100%;");
        var p1 = document.createElement("p");
        p1.setAttribute("class", "item-text item-name");
        var t1 = document.createTextNode(exams[i].name);
        p1.appendChild(t1);
        div.appendChild(p1);
        
        fo = document.createElementNS("http://www.w3.org/2000/svg", "foreignObject");
        fo.setAttribute("x", x);
        fo.setAttribute("y", y);
        fo.setAttribute("width", w / n_cols);
        fo.setAttribute("height", 3 / 2 * h / n_rows);
        
        fo.append(div);
        
        svg.append(fo);
    }

    return svg;
}
