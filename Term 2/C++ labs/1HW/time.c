#include <stdio.h>
#include <stdbool.h>

struct Date {
    int day;
    int month;
    int year;
};

bool is_leap_year(int year) {
    if (year % 400 == 0) {
        return true;
    }
    if (year % 100 == 0) {
        return false;
    }
    if (year % 4 == 0) {
        return true;
    }
    return false;
}

struct Date get_date(struct Date date, int diff) {
    int days_in_month[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    if (is_leap_year(date.year)) {
        days_in_month[1] = 29;
    }
    date.day += diff;
    while (date.day > days_in_month[date.month - 1]) {
        date.day -= days_in_month[date.month - 1];
        date.month++;
        if (date.month > 12) {
            date.month = 1;
            date.year++;
            if (is_leap_year(date.year)) {
                days_in_month[1] = 29;
            } else {
                days_in_month[1] = 28;
            }
        }
    }
    return date;
}


int main() {
    int hours, mins, secs;
    int date, month, year;
    long long diff;
    scanf("%d:%d:%d %d-%d-%d", &hours, &mins, &secs, &date, &month, &year);
    scanf("%lld", &diff);
    long long total_secs = hours * 3600 + mins * 60 + secs + diff;
    struct Date start_date = {date, month, year};
    start_date = get_date(start_date, (total_secs / (24 * 3600)));
    total_secs %= (24 * 3600);
    date = start_date.day;
    month = start_date.month;
    year = start_date.year;
    hours = total_secs / 3600;
    total_secs %= 3600;
    mins = total_secs / 60;
    secs = total_secs % 60;
    printf("%02d:%02d:%02d %02d-%02d-%04d\n", hours, mins, secs, date, month, year);
    return 0;
}