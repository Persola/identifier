if ls data/pagecount_totals/*.bz2 1> /dev/null 2>&1; then
    bunzip2 data/pagecount_totals/*.bz2
fi
rm -f data/pagecount_totals/filtered
sed -n 's/^\(en\.z .*\)/\1/p' data/pagecount_totals/pagecounts-*-totals >> data/pagecount_totals/filtered
