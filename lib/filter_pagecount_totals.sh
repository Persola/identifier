if ls data/monthly_view_totals/*.bz2 1> /dev/null 2>&1; then
    bunzip2 data/monthly_view_totals/*.bz2
fi
rm -f data/monthly_view_totals/filtered
sed -n 's/^\(en\.z .*\)/\1/p' data/monthly_view_totals/pagecounts-*-totals >> data/monthly_view_totals/filtered
