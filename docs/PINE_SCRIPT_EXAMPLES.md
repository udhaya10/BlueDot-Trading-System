# Pine Script Examples for BlueDot Trading System

This guide shows how to use the processed CSV data in TradingView using Pine Script.

## Automation Schedule

The system automatically processes data at:
- **Daily Processing**: 9:00 AM UTC every day (4 AM EST / 1 AM PST / 2:30 PM IST)
- **Weekly Processing**: 10:00 AM UTC every Sunday (5 AM EST / 2 AM PST / 3:30 PM IST)
- **Manual Trigger**: Available anytime via GitHub Actions tab

## Dataset Naming Convention

All datasets follow this format:
```
namespace_timeframe_SYMBOL
```

Where:
- **namespace**: `stocks_chimmu_ms` (your configured namespace)
- **timeframe**: `daily` or `weekly`
- **SYMBOL**: Stock symbol (e.g., AAPL, MSFT)

Each dataset contains columns:
- **BLUE_DOTS**: Binary trading signals (1=signal, 0=no signal)
- **RLST_RATING**: Relative Strength ratings (0-99)
- **BC_INDICATOR**: Base Count consolidation strength

## 1. RLST Rating Indicator

Display RLST (Relative Strength) ratings on a separate panel:

```pine
//@version=5
indicator("RLST Rating", overlay=false)

// Request RLST data
rlst_data = request.seed(
    dataset="stocks_chimmu_ms_daily_AAPL",
    symbol="RLST_RATING",
    close
)

// Plot RLST Rating (0-99 scale)
plot(rlst_data, title="RLST Rating", color=color.blue, linewidth=2)

// Add reference lines
hline(80, "Strong (80)", color=color.green, linestyle=hline.style_dashed)
hline(50, "Neutral (50)", color=color.gray, linestyle=hline.style_dashed)
hline(20, "Weak (20)", color=color.red, linestyle=hline.style_dashed)

// Color background based on strength
bgcolor(rlst_data >= 80 ? color.new(color.green, 90) : 
        rlst_data >= 50 ? color.new(color.yellow, 90) : 
        color.new(color.red, 90))

// Add alerts
alertcondition(crossover(rlst_data, 80), title="RLST Strong", message="RLST crossed above 80")
alertcondition(crossunder(rlst_data, 20), title="RLST Weak", message="RLST crossed below 20")
```

## 2. Blue Dot Trading Signals

Display blue dot buy signals on the price chart:

```pine
//@version=5
indicator("Blue Dot Signals", overlay=true)

// Request blue dot data
blue_dots = request.seed(
    dataset="stocks_chimmu_ms_daily_AAPL",
    symbol="BLUE_DOTS",
    close
)

// Plot blue dots when signal is 1
plotshape(blue_dots == 1, 
    title="Blue Dot Signal",
    style=shape.circle,
    location=location.belowbar,
    color=color.blue,
    size=size.small
)

// Add alert for new blue dots
alertcondition(blue_dots == 1, title="Blue Dot Signal", message="New Blue Dot signal detected")

// Show label with count
var label info_label = na
label.delete(info_label)
dot_count = ta.cum(blue_dots)
info_label := label.new(bar_index, high, 
    "Blue Dots: " + str.tostring(dot_count), 
    style=label.style_label_down,
    color=color.blue,
    textcolor=color.white
)
```

## 3. BC (Base Count) Indicator

Display BC consolidation strength indicator:

```pine
//@version=5
indicator("BC Indicator", overlay=false)

// Request BC data
bc_data = request.seed(
    dataset="stocks_chimmu_ms_daily_AAPL",
    symbol="BC_INDICATOR",
    close
)

// Plot BC values
plot(bc_data, title="BC Indicator", color=color.orange, linewidth=2)

// Add moving average
bc_ma = ta.sma(bc_data, 20)
plot(bc_ma, title="BC MA(20)", color=color.purple, linewidth=1)

// Highlight consolidation zones
bgcolor(bc_data > bc_ma ? color.new(color.green, 90) : color.new(color.red, 90))
```

## 4. Complete Trading System

Combine all indicators into a comprehensive trading system:

```pine
//@version=5
indicator("BlueDot Complete System", overlay=true)

// Input for symbol selection
symbol_input = input.string("AAPL", title="Stock Symbol")

// Construct dataset name
dataset_name = "stocks_chimmu_ms_daily_" + symbol_input

// Request all data from the same dataset
rlst = request.seed(dataset_name, "RLST_RATING", close)
bc = request.seed(dataset_name, "BC_INDICATOR", close)
blue_dots = request.seed(dataset_name, "BLUE_DOTS", close)

// Color bars based on RLST strength
barcolor(rlst >= 80 ? color.green : 
         rlst >= 50 ? color.yellow : 
         color.red,
         title="RLST Strength")

// Plot blue dot signals
plotshape(blue_dots == 1, 
    title="Blue Dot",
    style=shape.circle,
    location=location.belowbar,
    color=color.blue,
    size=size.normal
)

// Add info table
var table info_table = table.new(position.top_right, 2, 3)
if barstate.islast
    table.cell(info_table, 0, 0, "RLST", bgcolor=color.gray)
    table.cell(info_table, 1, 0, str.tostring(rlst, "#.#"), 
               bgcolor=rlst >= 80 ? color.green : rlst >= 50 ? color.yellow : color.red)
    
    table.cell(info_table, 0, 1, "BC", bgcolor=color.gray)
    table.cell(info_table, 1, 1, str.tostring(bc, "#.#"), bgcolor=color.orange)
    
    table.cell(info_table, 0, 2, "Signal", bgcolor=color.gray)
    table.cell(info_table, 1, 2, blue_dots == 1 ? "BUY" : "-", 
               bgcolor=blue_dots == 1 ? color.blue : color.gray)

// Trading alerts
alertcondition(blue_dots == 1 and rlst >= 80, 
    title="Strong Buy Signal", 
    message="Blue Dot + RLST > 80")
```

## 5. Multi-Timeframe Analysis

Compare daily and weekly data:

```pine
//@version=5
indicator("Multi-Timeframe RLST", overlay=false)

symbol = "AAPL"

// Daily RLST
daily_rlst = request.seed(
    "stocks_chimmu_ms_daily_" + symbol,
    "RLST_RATING",
    close
)

// Weekly RLST
weekly_rlst = request.seed(
    "stocks_chimmu_ms_weekly_" + symbol,
    "RLST_RATING",
    close
)

// Plot both timeframes
plot(daily_rlst, title="Daily RLST", color=color.blue, linewidth=2)
plot(weekly_rlst, title="Weekly RLST", color=color.purple, linewidth=3)

// Show divergence
divergence = daily_rlst - weekly_rlst
plot(divergence, title="Divergence", color=color.gray, style=plot.style_columns)
hline(0, "Zero", color=color.black)
```

## 6. Scanning for Opportunities

Create a scanner to find stocks with specific conditions:

```pine
//@version=5
indicator("BlueDot Scanner", overlay=false)

// List of symbols to scan
symbols = array.from("AAPL", "MSFT", "GOOGL", "AMZN", "TSLA")
results = array.new<string>()

// Check each symbol
for i = 0 to array.size(symbols) - 1
    sym = array.get(symbols, i)
    
    // Get RLST and Blue Dots for this symbol
    dataset = "stocks_chimmu_ms_daily_" + sym
    rlst = request.seed(dataset, "RLST_RATING", close)
    dots = request.seed(dataset, "BLUE_DOTS", close)
    
    // Check conditions
    if rlst >= 80 and dots == 1
        array.push(results, sym + " ✓")

// Display results
var table scan_table = table.new(position.middle_right, 1, array.size(symbols) + 1)
if barstate.islast
    table.cell(scan_table, 0, 0, "Strong Signals", bgcolor=color.blue, text_color=color.white)
    for i = 0 to array.size(results) - 1
        table.cell(scan_table, 0, i + 1, array.get(results, i), bgcolor=color.green)
```

## Tips for Using the Data

1. **Data Availability**: Ensure your GitHub Actions have run and data is deployed to GitHub Pages
2. **Timeframe Matching**: Use daily data on daily charts, weekly on weekly charts
3. **Symbol Case**: Use uppercase symbols (AAPL, not aapl)
4. **Error Handling**: Check if data exists before using:
   ```pine
   rlst = request.seed(dataset, "RLST", close)
   if not na(rlst)
       plot(rlst)
   ```

## Common Issues

1. **No data showing**: 
   - Check if CSV files are deployed to GitHub Pages
   - Verify dataset name matches exactly
   - Ensure you're using the correct timeframe

2. **Wrong values**: 
   - BC and RLST values should match your JSON data
   - Blue dots should be 1 or 0 only

3. **Performance**: 
   - Limit the number of request.seed() calls
   - Use higher timeframes for historical analysis