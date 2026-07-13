# The Comprehensive Finance Reference Guide

### A Complete Handbook for Financial Concepts, Markets, and Instruments

---

> **Document Purpose:** This reference guide covers foundational to advanced financial concepts including capital markets, corporate finance, risk management, derivatives, portfolio theory, and macroeconomic indicators. Designed for practitioners, analysts, and learners seeking a structured deep-dive into modern finance.

---

## Table of Contents

1. [Financial Markets Overview](#1-financial-markets-overview)
2. [Time Value of Money](#2-time-value-of-money)
3. [Equity Markets and Stock Valuation](#3-equity-markets-and-stock-valuation)
4. [Fixed Income and Bond Markets](#4-fixed-income-and-bond-markets)
5. [Derivatives: Options, Futures, and Swaps](#5-derivatives-options-futures-and-swaps)
6. [Portfolio Theory and Asset Allocation](#6-portfolio-theory-and-asset-allocation)
7. [Corporate Finance and Capital Structure](#7-corporate-finance-and-capital-structure)
8. [Financial Statement Analysis](#8-financial-statement-analysis)
9. [Risk Management](#9-risk-management)
10. [Macroeconomics and Monetary Policy](#10-macroeconomics-and-monetary-policy)
11. [Alternative Investments](#11-alternative-investments)
12. [FinTech and Digital Finance](#12-fintech-and-digital-finance)
13. [Behavioral Finance](#13-behavioral-finance)
14. [Key Financial Ratios Quick Reference](#14-key-financial-ratios-quick-reference)

---

## 1. Financial Markets Overview

### 1.1 What is a Financial Market?

A **financial market** is a mechanism that allows buyers and sellers to trade financial instruments such as stocks, bonds, currencies, and derivatives. Financial markets serve several critical economic functions:

- **Price Discovery:** Markets aggregate information from millions of participants to establish fair prices for assets.
- **Liquidity Provision:** Investors can convert assets to cash quickly and at predictable prices.
- **Capital Allocation:** Markets channel savings from households and institutions to productive investments.
- **Risk Transfer:** Through derivatives and insurance products, financial markets allow risk to be redistributed to those best able to bear it.
- **Information Aggregation:** Prices reflect the collective beliefs of all market participants about future cash flows.

### 1.2 Types of Financial Markets

#### Primary vs. Secondary Markets

| Feature        | Primary Market                              | Secondary Market                              |
| -------------- | ------------------------------------------- | --------------------------------------------- |
| Definition     | Where new securities are first issued       | Where previously issued securities are traded |
| Participants   | Issuers (companies/governments) + investors | Buyers and sellers (investors)                |
| Proceeds go to | The issuing company/entity                  | The selling investor                          |
| Examples       | IPOs, Bond Issuances, Rights Issues         | NYSE, NASDAQ, BSE, NSE                        |
| Price Setting  | Fixed or book-built                         | Determined by supply and demand               |

#### Capital Markets vs. Money Markets

**Capital Markets** deal in long-term instruments (maturity > 1 year):

- Equity (stocks)
- Long-term bonds
- Mortgage-backed securities

**Money Markets** deal in short-term instruments (maturity ≤ 1 year):

- Treasury Bills (T-Bills)
- Commercial Paper (CP)
- Certificates of Deposit (CDs)
- Repurchase Agreements (Repos)
- Federal Funds

### 1.3 Market Participants

**Buy-Side Institutions** (those who buy securities):

- Mutual Funds
- Pension Funds
- Hedge Funds
- Insurance Companies
- Sovereign Wealth Funds
- Retail Investors

**Sell-Side Institutions** (those who facilitate transactions):

- Investment Banks (Goldman Sachs, Morgan Stanley, JPMorgan)
- Broker-Dealers
- Market Makers
- Commercial Banks

**Regulatory Bodies:**

- **USA:** SEC (Securities and Exchange Commission), CFTC, FINRA, Federal Reserve
- **India:** SEBI (Securities and Exchange Board of India), RBI, IRDAI
- **UK:** FCA (Financial Conduct Authority), Bank of England
- **EU:** ESMA (European Securities and Markets Authority), ECB

### 1.4 Market Efficiency — The Efficient Market Hypothesis (EMH)

Developed by Eugene Fama in 1970, the **Efficient Market Hypothesis** states that asset prices fully reflect all available information at any given time. EMH has three forms:

| Form                 | Information Reflected               | Implication                                         |
| -------------------- | ----------------------------------- | --------------------------------------------------- |
| **Weak Form**        | All past trading prices and volumes | Technical analysis cannot produce alpha             |
| **Semi-Strong Form** | All publicly available information  | Fundamental analysis cannot produce sustained alpha |
| **Strong Form**      | All information (public + private)  | Even insider information is priced in               |

**Challenges to EMH:**

- Anomalies like the January Effect, momentum, and value premiums
- Bubbles and crashes (Dot-com 2000, Housing 2008)
- Behavioral finance evidence

---

## 2. Time Value of Money

### 2.1 The Core Principle

The **Time Value of Money (TVM)** is perhaps the single most important concept in finance. It states that **a rupee (or dollar) today is worth more than a rupee tomorrow**, because:

1. **Opportunity Cost:** Money available now can be invested to earn a return.
2. **Inflation:** Purchasing power erodes over time.
3. **Risk:** Future cash flows are uncertain.

### 2.2 Future Value (FV)

The **Future Value** is the amount a current sum grows to over time at a given interest rate.

**Single Cash Flow:**

```
FV = PV × (1 + r)^n
```

Where:

- `PV` = Present Value
- `r` = Interest rate per period
- `n` = Number of periods

**Example:** ₹10,000 invested at 8% per annum for 5 years:

```
FV = 10,000 × (1 + 0.08)^5
FV = 10,000 × 1.4693
FV = ₹14,693.28
```

**With Continuous Compounding:**

```
FV = PV × e^(r×t)
```

### 2.3 Present Value (PV)

**Present Value** is the current worth of a future sum of money discounted at a specific rate.

```
PV = FV / (1 + r)^n
```

**Example:** What is the present value of ₹50,000 to be received in 7 years, with a discount rate of 10%?

```
PV = 50,000 / (1 + 0.10)^7
PV = 50,000 / 1.9487
PV = ₹25,658.19
```

### 2.4 Annuities

An **annuity** is a series of equal cash flows at regular intervals.

**Present Value of Annuity:**

```
PV_annuity = PMT × [1 - (1 + r)^(-n)] / r
```

**Future Value of Annuity:**

```
FV_annuity = PMT × [(1 + r)^n - 1] / r
```

**Perpetuity (infinite annuity):**

```
PV_perpetuity = PMT / r
```

**Growing Perpetuity (Gordon Growth Model):**

```
PV = PMT / (r - g)
```

Where `g` is the constant growth rate in cash flows.

### 2.5 Net Present Value (NPV) and Internal Rate of Return (IRR)

**NPV** is used to evaluate investment projects:

```
NPV = Σ [CF_t / (1 + r)^t] - Initial Investment
```

**Decision Rule:**

- NPV > 0 → Accept the project (value-creating)
- NPV < 0 → Reject the project (value-destroying)
- NPV = 0 → Break-even

**IRR** is the discount rate at which NPV = 0. It represents the project's expected rate of return:

- If IRR > WACC (hurdle rate) → Accept
- If IRR < WACC → Reject

**IRR Limitations:**

- Multiple IRRs can exist for non-conventional cash flows
- Ignores project scale (can favor smaller high-return projects over larger value-creating ones)
- Assumes reinvestment at the IRR itself (unrealistic)

---

## 3. Equity Markets and Stock Valuation

### 3.1 Understanding Equity

**Equity** represents ownership in a company. Shareholders are residual claimants — they receive what is left after all other obligations (debt, taxes, preferred dividends) are paid.

**Types of Shares:**

- **Common Stock (Ordinary Shares):** Voting rights, residual claims on earnings
- **Preferred Stock:** Fixed dividend, no voting rights, priority over common in liquidation
- **American Depositary Receipts (ADRs):** Foreign company shares traded on US exchanges
- **Global Depositary Receipts (GDRs):** Similar, traded on international exchanges

### 3.2 Stock Exchanges

| Exchange                       | Country   | Founded | Notable Index                |
| ------------------------------ | --------- | ------- | ---------------------------- |
| New York Stock Exchange (NYSE) | USA       | 1792    | Dow Jones Industrial Average |
| NASDAQ                         | USA       | 1971    | NASDAQ Composite             |
| London Stock Exchange (LSE)    | UK        | 1801    | FTSE 100                     |
| Tokyo Stock Exchange (TSE)     | Japan     | 1878    | Nikkei 225                   |
| National Stock Exchange (NSE)  | India     | 1992    | NIFTY 50                     |
| Bombay Stock Exchange (BSE)    | India     | 1875    | SENSEX                       |
| Shanghai Stock Exchange        | China     | 1990    | SSE Composite                |
| Hong Kong Exchange (HKEX)      | Hong Kong | 1891    | Hang Seng Index              |

### 3.3 Stock Valuation Models

#### Dividend Discount Model (DDM)

The value of a stock equals the present value of all future dividends.

**Gordon Growth Model (Constant Growth DDM):**

```
P₀ = D₁ / (r - g)
```

Where:

- `P₀` = Current stock price
- `D₁` = Expected dividend next year
- `r` = Required rate of return
- `g` = Constant dividend growth rate

**Multi-Stage DDM:** Used when dividends grow at different rates during different phases.

#### Discounted Cash Flow (DCF) Valuation

```
Intrinsic Value = Σ [FCF_t / (1 + WACC)^t] + Terminal Value / (1 + WACC)^n
```

**Terminal Value Calculation:**

```
TV = FCF_n × (1 + g) / (WACC - g)    [Gordon Growth Method]
TV = EBITDA_n × Exit Multiple          [Exit Multiple Method]
```

#### Relative Valuation (Multiples)

| Multiple  | Formula                      | Typical Use                       |
| --------- | ---------------------------- | --------------------------------- |
| P/E Ratio | Price / Earnings per Share   | General equity valuation          |
| P/B Ratio | Price / Book Value per Share | Banks, asset-heavy companies      |
| EV/EBITDA | Enterprise Value / EBITDA    | Cross-industry comparison         |
| EV/Sales  | Enterprise Value / Revenue   | High-growth, pre-profit companies |
| P/FCF     | Price / Free Cash Flow       | Cash-generative businesses        |
| PEG Ratio | P/E / EPS Growth Rate        | Growth-adjusted valuation         |

### 3.4 Market Capitalization Categories

| Category  | Market Cap (USD) | Examples                 |
| --------- | ---------------- | ------------------------ |
| Mega Cap  | > $200 billion   | Apple, Microsoft, Aramco |
| Large Cap | $10B - $200B     | IBM, Ford, Pfizer        |
| Mid Cap   | $2B - $10B       | Varied across sectors    |
| Small Cap | $300M - $2B      | Regional companies       |
| Micro Cap | $50M - $300M     | Early-stage companies    |
| Nano Cap  | < $50M           | Penny stocks             |

### 3.5 Technical Analysis vs. Fundamental Analysis

**Fundamental Analysis:**

- Examines financial statements, industry dynamics, macroeconomic conditions
- Estimates intrinsic value
- Time horizon: Long-term (months to years)
- Practitioners: Warren Buffett, Benjamin Graham (Value Investing)

**Technical Analysis:**

- Studies price charts, patterns, and trading volume
- Identifies trends and momentum
- Key tools: Moving Averages, RSI, MACD, Bollinger Bands, Fibonacci Retracements
- Time horizon: Short to medium-term

**Common Technical Patterns:**

- Head and Shoulders (bearish reversal)
- Double Bottom (bullish reversal)
- Cup and Handle (bullish continuation)
- Descending Triangle (bearish continuation)

---

## 4. Fixed Income and Bond Markets

### 4.1 What is a Bond?

A **bond** is a debt instrument where the issuer borrows money from investors and agrees to pay:

1. **Coupon payments** — periodic interest payments (semi-annual in the US, annual in India/Europe)
2. **Face value (par value)** — typically ₹1,000 or $1,000, repaid at maturity

**Key Bond Terminology:**

| Term                    | Definition                                                         |
| ----------------------- | ------------------------------------------------------------------ |
| Face Value / Par Value  | Principal amount returned at maturity                              |
| Coupon Rate             | Annual interest rate as % of face value                            |
| Coupon Payment          | Coupon Rate × Face Value (periodic)                                |
| Maturity Date           | Date when principal is returned                                    |
| Yield to Maturity (YTM) | Total return if held to maturity                                   |
| Current Yield           | Annual Coupon / Current Price                                      |
| Duration                | Weighted average time to receive cash flows (sensitivity to rates) |
| Convexity               | Curvature of price-yield relationship                              |

### 4.2 Types of Bonds

**By Issuer:**

- **Government Bonds:** G-Secs (India), Treasuries (USA), Gilts (UK)
- **Municipal Bonds:** Issued by state/local governments
- **Corporate Bonds:** Investment-grade vs. High-yield (Junk bonds)
- **Supranational Bonds:** World Bank, IMF, ADB issued bonds

**By Structure:**

- **Zero-Coupon Bonds:** Issued at discount, no periodic payments
- **Floating Rate Notes (FRNs):** Coupon tied to a benchmark (LIBOR, SOFR, MIBOR)
- **Callable Bonds:** Issuer can redeem before maturity
- **Putable Bonds:** Investor can demand early repayment
- **Convertible Bonds:** Can be converted into equity at a specified price

**By Maturity:**

- **Bills / T-Bills:** < 1 year
- **Notes:** 1–10 years
- **Bonds:** > 10 years (30-year bonds are common)
- **Perpetuals / Consols:** No maturity, pay coupons forever

### 4.3 Bond Pricing

The price of a bond is the present value of all future cash flows:

```
Bond Price = Σ [C / (1 + r)^t] + [F / (1 + r)^n]
```

Where:

- `C` = Periodic coupon payment
- `F` = Face value
- `r` = Required yield (YTM) per period
- `n` = Total number of periods

**Bond Price and Yield Relationship (Inverse):**

- If YTM > Coupon Rate → Bond trades at a **Discount** (Price < Par)
- If YTM = Coupon Rate → Bond trades at **Par** (Price = Par)
- If YTM < Coupon Rate → Bond trades at a **Premium** (Price > Par)

### 4.4 Duration and Interest Rate Risk

**Macaulay Duration** measures the weighted average time (in years) to receive cash flows. It quantifies interest rate sensitivity.

```
Macaulay Duration = Σ [t × PV(CF_t)] / Bond Price
```

**Modified Duration:**

```
Modified Duration = Macaulay Duration / (1 + YTM/m)
```

**Price Change Approximation:**

```
ΔP/P ≈ -Modified Duration × Δy
```

**Example:** A bond with Modified Duration = 7.5 will fall approximately 7.5% in price if yields rise by 1%.

**Convexity** corrects for the non-linear price-yield relationship:

```
ΔP/P ≈ -D* × Δy + (1/2) × Convexity × (Δy)²
```

Higher convexity is beneficial to bondholders (upside greater, downside smaller).

### 4.5 The Yield Curve

The **yield curve** plots bond yields against their maturities. It signals economic expectations:

| Yield Curve Shape           | Description              | Economic Signal                           |
| --------------------------- | ------------------------ | ----------------------------------------- |
| Normal (Upward Sloping)     | Short rates < Long rates | Healthy economic growth expected          |
| Inverted (Downward Sloping) | Short rates > Long rates | Recession warning (historically reliable) |
| Flat                        | Short rates ≈ Long rates | Economic transition, uncertainty          |
| Humped                      | Medium rates highest     | Complex expectations                      |

**Credit Spread** = Corporate Bond Yield − Risk-Free (Government) Bond Yield

- Wider spreads signal higher perceived credit risk

### 4.6 Credit Ratings

| Moody's          | S&P / Fitch     | Category                                           |
| ---------------- | --------------- | -------------------------------------------------- |
| Aaa              | AAA             | Highest quality                                    |
| Aa1, Aa2, Aa3    | AA+, AA, AA−    | High quality                                       |
| A1, A2, A3       | A+, A, A−       | Upper medium grade                                 |
| Baa1, Baa2, Baa3 | BBB+, BBB, BBB− | Lower medium grade (**Investment Grade boundary**) |
| Ba1, Ba2         | BB+, BB         | Speculative / **High Yield (Junk)** begins         |
| B1–B3            | B+, B, B−       | Highly speculative                                 |
| Caa–C            | CCC–C           | Near default / In default                          |
| D                | D               | Default                                            |

---

## 5. Derivatives: Options, Futures, and Swaps

### 5.1 What are Derivatives?

A **derivative** is a financial contract whose value is derived from an underlying asset. Underlying assets include:

- Equities (individual stocks, indices)
- Commodities (gold, oil, wheat)
- Currencies (USD/INR, EUR/USD)
- Interest rates
- Credit events

**Purposes of Derivatives:**

1. **Hedging:** Reduce risk exposure
2. **Speculation:** Profit from price movements with leverage
3. **Arbitrage:** Exploit price discrepancies

### 5.2 Forward Contracts

A **forward contract** is a customized agreement to buy/sell an asset at a specified price on a future date.

- Traded **OTC** (over-the-counter), not on exchanges
- Customizable in size, date, and delivery location
- Carries **counterparty risk**
- Common in currencies (FX Forwards) and commodities

**Forward Price Formula:**

```
F₀ = S₀ × e^(r-q)T
```

Where:

- `S₀` = Current spot price
- `r` = Risk-free rate
- `q` = Dividend yield / convenience yield
- `T` = Time to expiry (in years)

### 5.3 Futures Contracts

**Futures** are standardized, exchange-traded forward contracts with daily mark-to-market settlement.

| Feature           | Forward         | Futures                          |
| ----------------- | --------------- | -------------------------------- |
| Trading venue     | OTC             | Exchange (NSE, CME, NYMEX)       |
| Standardization   | Customizable    | Standardized (size, date)        |
| Counterparty Risk | Yes             | No (Clearinghouse steps in)      |
| Settlement        | End of contract | Daily (MTM)                      |
| Margin            | Not required    | Required (Initial + Maintenance) |

**Key Futures Markets:**

- **Equity Index Futures:** NIFTY50, S&P 500, DAX
- **Commodity Futures:** Crude Oil (WTI, Brent), Gold, Silver, Natural Gas
- **Currency Futures:** USD/INR, EUR/USD
- **Interest Rate Futures:** 10-Year T-Bond Futures

### 5.4 Options

An **option** gives the buyer the **right, but not the obligation**, to buy or sell an asset at a predetermined price (strike price) on or before a specific date.

**Types of Options:**

- **Call Option:** Right to **BUY** the underlying
- **Put Option:** Right to **SELL** the underlying

**Option Styles:**

- **American:** Can be exercised any time before expiry
- **European:** Can only be exercised at expiry

**Option Profit/Loss:**

| Position   | When Profitable                    | Max Profit       | Max Loss         |
| ---------- | ---------------------------------- | ---------------- | ---------------- |
| Long Call  | Stock rises above Strike + Premium | Unlimited        | Premium paid     |
| Short Call | Stock stays below Strike           | Premium received | Unlimited        |
| Long Put   | Stock falls below Strike − Premium | Strike − Premium | Premium paid     |
| Short Put  | Stock stays above Strike           | Premium received | Strike − Premium |

### 5.5 The Black-Scholes Model

Developed in 1973 by Fischer Black, Myron Scholes, and Robert Merton, the **Black-Scholes model** prices European options.

**Call Option Price:**

```
C = S₀N(d₁) - Ke^(-rT)N(d₂)
```

**Put Option Price:**

```
P = Ke^(-rT)N(-d₂) - S₀N(-d₁)
```

Where:

```
d₁ = [ln(S₀/K) + (r + σ²/2)T] / (σ√T)
d₂ = d₁ - σ√T
```

- `S₀` = Current stock price
- `K` = Strike price
- `T` = Time to expiry
- `r` = Risk-free rate
- `σ` = Volatility (standard deviation of returns)
- `N(·)` = Cumulative normal distribution function

### 5.6 The Greeks

The **Greeks** measure an option's sensitivity to various parameters:

| Greek | Symbol | Measures                               | Typical Values                        |
| ----- | ------ | -------------------------------------- | ------------------------------------- |
| Delta | Δ      | Price change per $1 move in underlying | Calls: 0 to 1, Puts: -1 to 0          |
| Gamma | Γ      | Rate of change of Delta                | Highest ATM, near expiry              |
| Theta | Θ      | Time decay (value lost per day)        | Negative for long options             |
| Vega  | ν      | Sensitivity to volatility change       | Positive for long options             |
| Rho   | ρ      | Sensitivity to interest rate change    | Positive for calls, negative for puts |

### 5.7 Common Options Strategies

| Strategy         | Construction                                      | View                      | Max Profit              | Max Loss         |
| ---------------- | ------------------------------------------------- | ------------------------- | ----------------------- | ---------------- |
| Covered Call     | Long Stock + Short Call                           | Neutral to mildly bullish | Strike - Cost + Premium | Stock goes to 0  |
| Protective Put   | Long Stock + Long Put                             | Bullish but hedged        | Unlimited               | Limited by put   |
| Bull Call Spread | Long lower strike call + Short higher strike call | Moderately bullish        | Spread width - Premium  | Net premium      |
| Bear Put Spread  | Long higher strike put + Short lower strike put   | Moderately bearish        | Spread - Net Premium    | Net premium      |
| Straddle         | Long Call + Long Put (same strike)                | High volatility expected  | Unlimited               | Total premium    |
| Iron Condor      | Bull put spread + Bear call spread                | Low volatility expected   | Net premium             | Spread - premium |

### 5.8 Swaps

A **swap** is an agreement between two parties to exchange cash flows over time.

**Interest Rate Swap (IRS):**

- Party A pays a **fixed rate**, receives a **floating rate** (e.g., LIBOR/SOFR)
- Party B pays **floating**, receives **fixed**
- Used to manage interest rate exposure

**Currency Swap:**

- Exchange principal and interest payments in different currencies
- Used by multinationals to hedge FX exposure

**Credit Default Swap (CDS):**

- Buyer pays periodic premium; seller compensates if the reference entity defaults
- Functions like "insurance" on credit risk
- Played a major role in the 2008 financial crisis

---

## 6. Portfolio Theory and Asset Allocation

### 6.1 Modern Portfolio Theory (MPT)

Developed by Harry Markowitz in 1952, **Modern Portfolio Theory** formalizes how investors can construct optimal portfolios by balancing expected return and risk.

**Key Insight:** Through diversification, investors can reduce **unsystematic risk** (company-specific) without necessarily reducing expected returns.

**Expected Return of a Portfolio:**

```
E(Rp) = Σ wᵢ × E(Rᵢ)
```

**Portfolio Variance (two assets):**

```
σ²p = w₁²σ₁² + w₂²σ₂² + 2w₁w₂Cov(R₁,R₂)
σ²p = w₁²σ₁² + w₂²σ₂² + 2w₁w₂ρ₁₂σ₁σ₂
```

Where `ρ₁₂` is the correlation between assets 1 and 2.

**Diversification Benefit:**

- When ρ = +1: No diversification benefit
- When ρ = 0: Partial diversification benefit
- When ρ = -1: Maximum diversification (risk eliminated)

### 6.2 The Efficient Frontier

The **Efficient Frontier** is the set of portfolios that offer the highest expected return for a given level of risk.

- Portfolios **on** the frontier: Optimal (no more return without more risk)
- Portfolios **below** the frontier: Inefficient (dominated by frontier portfolios)
- Portfolios **above** the frontier: Impossible to achieve

**The Minimum Variance Portfolio (MVP)** is the point on the frontier with the lowest possible volatility.

### 6.3 Capital Market Line (CML) and CAPM

When a **risk-free asset** is introduced, the optimal portfolio combines the risk-free asset with the **Market Portfolio** (all risky assets in proportion to their market cap).

**Capital Market Line:**

```
E(Rp) = Rf + [(E(Rm) - Rf) / σm] × σp
```

**Capital Asset Pricing Model (CAPM):**

```
E(Ri) = Rf + βᵢ × [E(Rm) - Rf]
```

Where:

- `Rf` = Risk-free rate
- `βᵢ` = Beta of asset i (systematic risk measure)
- `E(Rm)` = Expected market return
- `[E(Rm) - Rf]` = Equity Risk Premium (ERP)

**Beta Interpretation:**

- β = 1: Asset moves in line with market
- β > 1: Asset is more volatile than market (aggressive)
- β < 1: Asset is less volatile (defensive)
- β < 0: Asset moves opposite to market (rare, e.g., inverse ETFs)

### 6.4 Alpha

**Alpha (α)** is the excess return of an investment above what CAPM predicts:

```
α = Actual Return - CAPM Expected Return
α = Ri - [Rf + β(Rm - Rf)]
```

Positive alpha indicates outperformance; it's the "holy grail" of active management.

### 6.5 Factor Models

**Fama-French Three-Factor Model (1992):**
Adds two factors to CAPM:

```
E(Ri) - Rf = β₁(Rm - Rf) + β₂(SMB) + β₃(HML)
```

- **SMB (Small Minus Big):** Small-cap stocks outperform large-cap
- **HML (High Minus Low):** Value stocks (high B/P) outperform growth stocks

**Carhart Four-Factor Model:** Adds **Momentum (MOM)** factor.

**Fama-French Five-Factor Model (2015):** Adds **Profitability (RMW)** and **Investment (CMA)** factors.

### 6.6 Asset Allocation Strategies

**Strategic Asset Allocation (SAA):** Long-term target weights (e.g., 60% equity, 40% bonds)

**Tactical Asset Allocation (TAA):** Short-term deviations from SAA to exploit market opportunities

**Dynamic Asset Allocation:** Continuously adjusts weights based on market conditions

**Risk Parity:** Allocates based on equal risk contribution from each asset class, not equal capital

**Example SAA by Investor Profile:**

| Profile                          | Equity | Fixed Income | Cash/Alternatives |
| -------------------------------- | ------ | ------------ | ----------------- |
| Aggressive (Young, Long Horizon) | 80%    | 15%          | 5%                |
| Moderate (Mid-Career)            | 60%    | 30%          | 10%               |
| Conservative (Near Retirement)   | 35%    | 55%          | 10%               |
| Capital Preservation             | 15%    | 70%          | 15%               |

---

## 7. Corporate Finance and Capital Structure

### 7.1 The Goal of Corporate Finance

The primary objective of financial management is to **maximize shareholder wealth**, which translates to maximizing the firm's stock price or intrinsic value. This involves three key decisions:

1. **Investment Decision (Capital Budgeting):** Which projects to invest in?
2. **Financing Decision (Capital Structure):** How to fund those investments?
3. **Dividend Decision:** How much of earnings to return to shareholders?

### 7.2 Capital Structure

**Capital structure** refers to the mix of debt and equity a company uses to finance its assets.

```
Total Assets = Total Debt + Total Equity
Enterprise Value = Market Cap + Net Debt
```

**Leverage Ratios:**

- Debt-to-Equity (D/E) = Total Debt / Total Equity
- Debt-to-Capital = Total Debt / (Debt + Equity)
- Interest Coverage = EBIT / Interest Expense

### 7.3 Modigliani-Miller Theorems

**Without taxes (1958):** Capital structure is irrelevant — firm value is independent of financing. A firm cannot change its total value by splitting cash flows differently between debt and equity.

**With taxes (1963):** Debt is beneficial because **interest payments are tax-deductible**, creating a "**tax shield**":

```
Value of Levered Firm = Value of Unlevered Firm + PV(Tax Shield)
Value of Levered Firm = VU + t×D
```

Where `t` = corporate tax rate, `D` = debt outstanding.

**Implication:** Firms should use as much debt as possible to maximize tax shields... but this ignores financial distress costs.

### 7.4 Trade-off Theory

The **Trade-off Theory** finds the optimal capital structure where:

```
Optimal Debt = Point where Marginal Benefit of Tax Shield = Marginal Cost of Financial Distress
```

**Costs of Financial Distress:**

- Direct costs: Legal/bankruptcy fees
- Indirect costs: Loss of customers, suppliers, employees; management distraction

### 7.5 Weighted Average Cost of Capital (WACC)

WACC is the blended cost of capital from all sources, used as the discount rate for firm-level DCF valuations:

```
WACC = (E/V) × Re + (D/V) × Rd × (1 - t)
```

Where:

- `E` = Market value of equity
- `D` = Market value of debt
- `V` = E + D (total firm value)
- `Re` = Cost of equity
- `Rd` = Cost of debt (pre-tax)
- `t` = Corporate tax rate

**Cost of Equity (using CAPM):**

```
Re = Rf + β × (Rm - Rf)
```

**Example WACC Calculation:**

- Equity = ₹600 Cr, Debt = ₹400 Cr, Total = ₹1,000 Cr
- Cost of Equity = 14%, Cost of Debt = 8%, Tax Rate = 25%

```
WACC = (600/1000) × 14% + (400/1000) × 8% × (1 - 0.25)
WACC = 0.60 × 14% + 0.40 × 6%
WACC = 8.4% + 2.4% = 10.8%
```

### 7.6 Dividend Policy

**Gordon Growth Model (revisited):** Dividends signal management's confidence in future earnings.

**Dividend Policy Types:**

- **Stable Dividend Policy:** Constant dividends; most common, preferred by income investors
- **Residual Dividend Policy:** Pay dividends only after all positive-NPV investments are funded
- **Constant Payout Ratio:** Fixed % of earnings each year
- **Zero Dividend / Share Buybacks:** Reinvest all earnings; prefer buybacks for tax efficiency

**Modigliani-Miller Dividend Irrelevance:** In perfect markets, dividend policy doesn't affect firm value — investors can create "homemade dividends" by selling shares.

**In practice:** Dividends and buybacks do matter due to taxes, signaling effects, and investor preferences.

### 7.7 Mergers and Acquisitions (M&A)

**Types of M&A:**

- **Horizontal Merger:** Same industry (e.g., two banks merging)
- **Vertical Merger:** Supply chain integration (e.g., manufacturer acquires supplier)
- **Conglomerate Merger:** Unrelated businesses
- **Acquisition:** One company buys another (friendly or hostile)
- **Leveraged Buyout (LBO):** Private equity buys company using high leverage

**Valuation in M&A:**

- Comparable Company Analysis (Comps)
- Precedent Transaction Analysis
- DCF Analysis
- Accretion/Dilution Analysis

**Synergies** = Additional value created by combining firms:

```
Deal Value = Standalone Value of Target + PV(Synergies) - Premium Paid
```

---

## 8. Financial Statement Analysis

### 8.1 The Three Core Financial Statements

Every public company must publish three core financial statements:

1. **Income Statement (P&L):** Shows revenues and expenses over a period
2. **Balance Sheet:** Shows assets, liabilities, and equity at a point in time
3. **Cash Flow Statement:** Shows cash inflows and outflows over a period

### 8.2 Income Statement Structure

```
Revenue (Net Sales)
- Cost of Goods Sold (COGS)
= Gross Profit
- Operating Expenses (SG&A, R&D, Depreciation)
= EBIT (Earnings Before Interest and Taxes)
- Interest Expense
= EBT (Earnings Before Tax)
- Income Tax Expense
= Net Income
- Preferred Dividends
= Earnings Available to Common Shareholders
÷ Shares Outstanding
= EPS (Earnings Per Share)
```

### 8.3 Balance Sheet Structure

**Assets = Liabilities + Shareholders' Equity**

| Assets                       | Liabilities & Equity             |
| ---------------------------- | -------------------------------- |
| **Current Assets**           | **Current Liabilities**          |
| Cash & Equivalents           | Accounts Payable                 |
| Accounts Receivable          | Short-term Debt                  |
| Inventory                    | Accrued Expenses                 |
| Prepaid Expenses             | Deferred Revenue                 |
| **Non-Current Assets**       | **Long-term Liabilities**        |
| Property, Plant & Equipment  | Long-term Debt                   |
| Intangible Assets (Goodwill) | Deferred Tax Liability           |
| Long-term Investments        | **Shareholders' Equity**         |
|                              | Common Stock + Retained Earnings |

### 8.4 Cash Flow Statement

**Three Sections:**

1. **Operating Activities:** Cash from core business operations (Net Income adjusted for non-cash items and working capital changes)
2. **Investing Activities:** Capital expenditures, acquisitions, asset sales
3. **Financing Activities:** Debt issuance/repayment, equity issuance, dividends paid

**Free Cash Flow (FCF):**

```
FCF = Operating Cash Flow - Capital Expenditures (CapEx)
```

**Unlevered FCF (for DCF):**

```
UFCF = EBIT × (1 - Tax Rate) + D&A - ΔWorking Capital - CapEx
```

### 8.5 Profitability Ratios

| Ratio                             | Formula                           | What It Measures                          |
| --------------------------------- | --------------------------------- | ----------------------------------------- |
| Gross Margin                      | Gross Profit / Revenue            | Efficiency of production/service delivery |
| Operating Margin (EBIT Margin)    | EBIT / Revenue                    | Core operational efficiency               |
| Net Profit Margin                 | Net Income / Revenue              | Overall bottom-line profitability         |
| Return on Assets (ROA)            | Net Income / Total Assets         | How well assets generate profit           |
| Return on Equity (ROE)            | Net Income / Shareholders' Equity | Return on equity capital                  |
| Return on Invested Capital (ROIC) | NOPAT / Invested Capital          | Quality of capital allocation             |
| EBITDA Margin                     | EBITDA / Revenue                  | Cash profitability (pre capex)            |

### 8.6 DuPont Analysis

**DuPont breaks ROE into component drivers:**

**3-Factor DuPont:**

```
ROE = Net Profit Margin × Asset Turnover × Financial Leverage
ROE = (NI/Sales) × (Sales/Assets) × (Assets/Equity)
```

**5-Factor DuPont:**

```
ROE = Tax Burden × Interest Burden × EBIT Margin × Asset Turnover × Leverage
```

This reveals whether ROE improvement comes from higher profitability, better asset efficiency, or increased leverage.

---

## 9. Risk Management

### 9.1 Types of Financial Risk

| Risk Type                       | Description                             | Examples                             |
| ------------------------------- | --------------------------------------- | ------------------------------------ |
| **Market Risk**                 | Loss from adverse market movements      | Stock decline, interest rate rise    |
| **Credit Risk**                 | Counterparty defaults on obligations    | Loan default, bond issuer bankruptcy |
| **Liquidity Risk**              | Cannot sell asset quickly at fair value | Illiquid bonds, real estate          |
| **Operational Risk**            | Losses from processes, systems, people  | Fraud, system failure, human error   |
| **Currency Risk (FX)**          | Losses from exchange rate movements     | USD/INR appreciation hurting exports |
| **Interest Rate Risk**          | Changes in rates affect portfolio value | Rising rates reducing bond prices    |
| **Inflation Risk**              | Real returns eroded by inflation        | Fixed-income investments             |
| **Political / Regulatory Risk** | Government actions affect investments   | Tax changes, nationalization         |
| **Model Risk**                  | Errors in models used for pricing/risk  | Incorrect Black-Scholes assumptions  |

### 9.2 Value at Risk (VaR)

**VaR** answers: "What is the maximum loss we can expect with X% confidence over Y days?"

**Definition:** At 95% confidence over 1 day, a VaR of ₹10 Cr means there is a 5% chance of losing more than ₹10 Cr in a single day.

**Three Approaches:**

1. **Historical Simulation:** Use actual historical returns to compute loss distribution
2. **Parametric (Delta-Normal) VaR:** Assumes normal distribution

   ```
   VaR = Portfolio Value × z-score × σ × √T
   ```

   (z = 1.645 for 95% confidence, 2.326 for 99%)

3. **Monte Carlo Simulation:** Simulate thousands of random scenarios

**Limitations of VaR:**

- Doesn't capture "tail risk" beyond the confidence level
- Assumes historical patterns continue
- Not sub-additive in all cases (violates diversification logic)

### 9.3 Expected Shortfall (CVaR)

**Expected Shortfall (ES)** / **Conditional VaR (CVaR)** measures the average loss _beyond_ the VaR threshold. It is considered superior to VaR for tail risk management.

```
CVaR₉₅% = Average of all losses exceeding the 95% VaR
```

### 9.4 Hedging Strategies

**Natural Hedging:** Matching revenues and costs in the same currency/rate environment (e.g., an Indian exporter borrowing in USD).

**Derivative Hedging:**

- **Futures/Forwards:** Lock in a future price
- **Options:** Asymmetric protection (like insurance)
- **Swaps:** Convert variable-rate to fixed-rate exposure (or vice versa)

**Hedge Ratio (for futures):**

```
Optimal Hedge Ratio = ρ × (σ_spot / σ_futures)
```

**Beta Hedging (equity portfolio):**

```
Number of Contracts = (β_target - β_portfolio) / β_futures × (Portfolio Value / Futures Value)
```

---

## 10. Macroeconomics and Monetary Policy

### 10.1 Key Macroeconomic Indicators

| Indicator                            | Measures                      | Data Source (India) |
| ------------------------------------ | ----------------------------- | ------------------- |
| GDP Growth Rate                      | Economic output growth        | MOSPI               |
| CPI Inflation                        | Consumer price level changes  | MoSPI / RBI         |
| WPI (Wholesale Price Index)          | Wholesale price changes       | DPIIT               |
| Repo Rate                            | RBI's key lending rate        | RBI                 |
| Unemployment Rate                    | Labour market slack           | CMIE / PLFS         |
| Current Account Deficit (CAD)        | Trade + income balance        | RBI                 |
| Fiscal Deficit                       | Government spending - Revenue | Budget Documents    |
| Foreign Exchange Reserves            | RBI's FX holdings             | RBI Weekly          |
| Index of Industrial Production (IIP) | Manufacturing activity        | MOSPI               |
| PMI (Purchasing Managers' Index)     | Business activity sentiment   | S&P Global          |

### 10.2 The Business Cycle

The economy moves through four phases:

1. **Expansion:** Rising GDP, falling unemployment, increasing corporate profits, stock markets typically rise
2. **Peak:** Maximum economic output, inflation risks rise, central bank tightens
3. **Contraction/Recession:** Falling GDP (two consecutive quarters), rising unemployment, credit tightens
4. **Trough:** Minimum output, central banks ease, recovery begins

**Cyclical vs. Defensive Sectors:**

| Cyclical (Benefit in Expansion) | Defensive (Hold in Contraction) |
| ------------------------------- | ------------------------------- |
| Consumer Discretionary          | Consumer Staples                |
| Industrials                     | Healthcare                      |
| Materials                       | Utilities                       |
| Technology                      | Pharmaceuticals                 |
| Financials                      | FMCG                            |

### 10.3 Monetary Policy

Central banks use monetary policy to achieve price stability and economic growth.

**RBI Policy Tools:**

- **Repo Rate:** Rate at which RBI lends to commercial banks (key policy rate)
- **Reverse Repo Rate:** Rate at which RBI borrows from commercial banks
- **Cash Reserve Ratio (CRR):** Mandatory % of deposits kept with RBI
- **Statutory Liquidity Ratio (SLR):** % of deposits in liquid assets (G-Secs, cash)
- **Open Market Operations (OMO):** Buying/selling G-Secs to inject/absorb liquidity
- **Marginal Standing Facility (MSF):** Emergency borrowing window

**Monetary Policy Stances:**

- **Accommodative:** Low rates, support growth (used during downturns)
- **Neutral:** Neither tightening nor easing
- **Hawkish:** Tightening bias, combat inflation
- **Withdrawal of Accommodation:** Gradual removal of stimulus

### 10.4 Inflation

**Inflation** is the rate at which the general price level increases over time.

**Causes:**

- **Demand-Pull:** Economy overheats, too much money chasing goods
- **Cost-Push:** Rising input costs (oil prices, wages) push prices up
- **Structural:** Supply bottlenecks, poor productivity

**Measures:**

- **CPI (Consumer Price Index):** Most common; tracks retail prices of a basket of goods
- **Core CPI:** Excludes food and fuel (volatile items)
- **WPI:** Tracks wholesale/producer price changes
- **PCE Deflator:** US Federal Reserve's preferred measure

**Fisher Equation:**

```
Nominal Interest Rate ≈ Real Interest Rate + Inflation Rate
(1 + nominal) = (1 + real) × (1 + inflation)
```

**Real Returns:**

```
Real Return = [(1 + Nominal Return) / (1 + Inflation Rate)] - 1
```

### 10.5 The Fiscal Policy

**Fiscal policy** involves government spending and taxation decisions.

**Expansionary Fiscal Policy:**

- Increase government spending
- Decrease taxes
- → Stimulates aggregate demand
- → Often leads to higher fiscal deficit

**Contractionary Fiscal Policy:**

- Decrease spending
- Increase taxes
- → Reduces inflationary pressures

**Fiscal Deficit:**

```
Fiscal Deficit = Total Expenditure - Total Receipts (excluding borrowings)
```

India's fiscal deficit target is typically ~4.5–5.1% of GDP (Fiscal Consolidation Road Map).

**Debt-to-GDP Ratio:** Measures government debt sustainability. IMF suggests < 60% for emerging markets is advisable.

---

## 11. Alternative Investments

### 11.1 What are Alternative Investments?

**Alternative investments** are asset classes outside traditional stocks, bonds, and cash. They are typically:

- Less liquid
- Higher returning over long horizons
- Less correlated with public markets
- Suitable for institutional investors and HNIs (High Net Worth Individuals)

### 11.2 Private Equity

Private equity involves investing in companies not listed on public exchanges.

**Types:**

- **Venture Capital (VC):** Early-stage startups (Seed, Series A/B/C)
- **Growth Equity:** Established companies seeking expansion capital
- **Leveraged Buyouts (LBO):** Acquiring mature companies using debt
- **Distressed/Special Situations:** Investing in financially troubled companies

**PE Returns Metrics:**

- **IRR (Internal Rate of Return):** Annualized return on invested capital
- **MOIC (Multiple on Invested Capital):** Total value / invested capital
- **DPI (Distributions to Paid-In Capital):** Cash returned / invested capital
- **RVPI (Residual Value to Paid-In):** Remaining unrealized value / invested capital
- **TVPI = DPI + RVPI**

**LBO Model Logic:**

```
Returns = f(Entry Multiple, Exit Multiple, Revenue Growth, Margin Expansion, Leverage)
```

### 11.3 Real Estate

**Real Estate Investment Types:**

- **Direct Ownership:** Residential, commercial, industrial properties
- **REITs (Real Estate Investment Trusts):** Liquid, exchange-listed exposure to real estate
- **Real Estate Debt:** Mortgage lending, mezzanine financing
- **Infrastructure:** Roads, airports, power plants, data centers

**Key RE Metrics:**

- **Cap Rate (Capitalization Rate):** NOI / Property Value (analogous to earnings yield)
- **NOI (Net Operating Income):** Revenue - Operating Expenses (before debt service)
- **Cash-on-Cash Return:** Annual Cash Flow / Cash Invested
- **LTV (Loan-to-Value):** Mortgage / Property Value

### 11.4 Hedge Funds

Hedge funds are lightly regulated investment vehicles that use sophisticated strategies to generate returns.

**Common Strategies:**

| Strategy              | Description                                                   | Risk/Return  |
| --------------------- | ------------------------------------------------------------- | ------------ |
| Long/Short Equity     | Long undervalued, short overvalued stocks                     | Moderate     |
| Global Macro          | Bets on macroeconomic trends (currencies, rates, commodities) | High         |
| Statistical Arbitrage | Quantitative pairs trading                                    | Low-Moderate |
| Event Driven          | Mergers, bankruptcies, spin-offs                              | Moderate     |
| Distressed Debt       | Buys bonds/loans of struggling companies                      | High         |
| Quantitative / CTA    | Algorithmic, trend-following strategies                       | Varies       |

**Fee Structure:** Typically "2 and 20" — 2% management fee + 20% performance fee above a hurdle rate.

### 11.5 Commodities

**Commodity Categories:**

- **Energy:** Crude Oil (WTI, Brent), Natural Gas, Coal
- **Precious Metals:** Gold, Silver, Platinum
- **Base Metals:** Copper, Aluminum, Zinc, Nickel
- **Agricultural:** Wheat, Corn, Soybeans, Sugar, Cotton
- **Soft Commodities:** Coffee, Cocoa, Orange Juice

**Gold in Finance:**

- Often seen as a **safe haven** during market stress
- **Inverse correlation** with USD (generally)
- **Store of value** against inflation
- Central bank reserves include significant gold holdings

---

## 12. FinTech and Digital Finance

### 12.1 The FinTech Revolution

**FinTech** (Financial Technology) refers to companies and technologies that improve financial services. Key areas include:

- **Digital Payments:** UPI (India), PayPal, Stripe, Square
- **Neobanks:** Digital-only banks (Revolut, N26, Fi Money, Jupiter)
- **InsurTech:** AI-driven insurance (Acko, Digit Insurance)
- **WealthTech:** Robo-advisors, digital wealth platforms (Zerodha, Groww, Smallcase)
- **LendingTech:** P2P lending, BNPL (Buy Now Pay Later)
- **RegTech:** Technology for regulatory compliance

### 12.2 Cryptocurrencies and Blockchain

**Blockchain** is a distributed ledger technology (DLT) where transactions are recorded in blocks chained cryptographically.

**Key Concepts:**

- **Proof of Work (PoW):** Miners solve computational puzzles (Bitcoin uses this)
- **Proof of Stake (PoS):** Validators stake crypto as collateral (Ethereum post-merge)
- **DeFi (Decentralized Finance):** Financial services without intermediaries
- **Smart Contracts:** Self-executing code on blockchain (Ethereum)
- **NFTs (Non-Fungible Tokens):** Unique digital assets on blockchain
- **Stablecoins:** Crypto pegged to a fiat currency (USDT, USDC, DAI)

**Major Cryptocurrencies:**

| Crypto       | Symbol | Market Cap (2024) | Use Case                       |
| ------------ | ------ | ----------------- | ------------------------------ |
| Bitcoin      | BTC    | ~$1.3 Trillion    | Digital gold, store of value   |
| Ethereum     | ETH    | ~$400 Billion     | Smart contracts, DeFi platform |
| Binance Coin | BNB    | ~$90 Billion      | Binance exchange utility       |
| Solana       | SOL    | ~$80 Billion      | High-speed blockchain          |
| Ripple       | XRP    | ~$60 Billion      | Cross-border payments          |

**Regulatory Landscape (India):**

- Crypto income taxed at 30% flat (Budget 2022)
- 1% TDS on crypto transactions
- RBI exploring a **CBDC (Central Bank Digital Currency)** — the Digital Rupee (e-₹)

### 12.3 Open Banking and APIs

**Open Banking** requires banks to share customer data (with consent) with third-party providers via APIs.

**India's Ecosystem:**

- **Account Aggregator (AA) Framework:** Consent-based financial data sharing
- **OCEN (Open Credit Enablement Network):** Democratizes credit access for MSMEs
- **UPI (Unified Payments Interface):** Real-time payment infrastructure processed by NPCI

---

## 13. Behavioral Finance

### 13.1 Why Markets Aren't Always Rational

**Behavioral finance** integrates psychology and economics to explain why investors often act irrationally. Key founding figures: Daniel Kahneman, Amos Tversky, Richard Thaler.

### 13.2 Common Cognitive Biases

| Bias                       | Description                                        | Example in Investing                                 |
| -------------------------- | -------------------------------------------------- | ---------------------------------------------------- |
| **Overconfidence**         | Investors overestimate their ability               | Excessive trading, underestimating risk              |
| **Anchoring**              | Over-reliance on first piece of information        | Fixating on a stock's 52-week high                   |
| **Confirmation Bias**      | Seeking information that confirms existing beliefs | Only reading bullish analysis                        |
| **Loss Aversion**          | Losses hurt ~2× more than gains feel good          | Holding losers too long, selling winners too early   |
| **Herding**                | Following the crowd                                | Buying at market peaks during euphoria               |
| **Mental Accounting**      | Treating money differently based on source         | Gambling with "house money" from market gains        |
| **Recency Bias**           | Overweighting recent events                        | Buying after a bull market thinking it will continue |
| **Availability Heuristic** | Judging probability by ease of recall              | Overestimating plane crash risk after news coverage  |
| **Sunk Cost Fallacy**      | Continuing bad investment because of past costs    | "I can't sell now, I'd lose money"                   |
| **Disposition Effect**     | Selling winners too early, holding losers too long | Combination of loss aversion + mental accounting     |

### 13.3 Prospect Theory

Developed by Kahneman and Tversky (1979), **Prospect Theory** is an alternative to Expected Utility Theory:

1. **Reference Dependence:** Outcomes evaluated as gains/losses relative to a reference point
2. **Loss Aversion:** Losses are felt more powerfully than equivalent gains
3. **Diminishing Sensitivity:** Each additional gain/loss matters less as it grows
4. **Probability Weighting:** People overweight small probabilities, underweight large ones

**Value Function:** Concave for gains (risk averse), convex for losses (risk seeking in loss domain).

---

## 14. Key Financial Ratios Quick Reference

### Profitability

| Ratio        | Formula                   | Good Level (General)                 |
| ------------ | ------------------------- | ------------------------------------ |
| Gross Margin | Gross Profit / Revenue    | Higher is better; varies by industry |
| Net Margin   | Net Income / Revenue      | Positive; > 10% is good              |
| ROE          | Net Income / Equity       | > 15% for most industries            |
| ROIC         | NOPAT / Invested Capital  | > WACC (value creation)              |
| ROA          | Net Income / Total Assets | > 5% generally                       |

### Liquidity

| Ratio                   | Formula                                            | Healthy Range |
| ----------------------- | -------------------------------------------------- | ------------- |
| Current Ratio           | Current Assets / Current Liabilities               | 1.5 – 3.0     |
| Quick Ratio (Acid Test) | (Current Assets - Inventory) / Current Liabilities | > 1.0         |
| Cash Ratio              | Cash / Current Liabilities                         | > 0.5         |

### Leverage / Solvency

| Ratio             | Formula                            | Note                            |
| ----------------- | ---------------------------------- | ------------------------------- |
| Debt-to-Equity    | Total Debt / Total Equity          | < 2.0 generally                 |
| Debt-to-EBITDA    | Total Debt / EBITDA                | < 3.0x generally; > 5x is risky |
| Interest Coverage | EBIT / Interest Expense            | > 3.0 (comfortable)             |
| Asset Coverage    | (Assets - Intangibles - CL) / Debt | > 1.5                           |

### Efficiency

| Ratio                        | Formula                    | Note                               |
| ---------------------------- | -------------------------- | ---------------------------------- |
| Asset Turnover               | Revenue / Total Assets     | Higher = better asset utilization  |
| Inventory Turnover           | COGS / Average Inventory   | Higher = faster inventory movement |
| Receivables Turnover         | Revenue / Average A/R      | Higher = faster collections        |
| Days Sales Outstanding (DSO) | 365 / Receivables Turnover | Lower = faster cash collection     |
| Cash Conversion Cycle (CCC)  | DIO + DSO - DPO            | Lower is better                    |

### Valuation

| Ratio          | Formula                   | Note                            |
| -------------- | ------------------------- | ------------------------------- |
| P/E Ratio      | Market Price / EPS        | Compare to sector average       |
| Forward P/E    | Price / Next Year EPS     | Forward-looking                 |
| PEG Ratio      | P/E / EPS Growth Rate     | < 1 may indicate undervaluation |
| P/B Ratio      | Market Cap / Book Value   | Banks: ~1–2 is typical          |
| EV/EBITDA      | Enterprise Value / EBITDA | 8–15x typical for most sectors  |
| Dividend Yield | Annual DPS / Stock Price  | Higher = more income            |

---

## Appendix: Key Finance Formulas Summary

```
──────────────────────────────────────────────────────────────────
TIME VALUE OF MONEY
──────────────────────────────────────────────────────────────────
Future Value:           FV = PV × (1 + r)^n
Present Value:          PV = FV / (1 + r)^n
PV Annuity:             PV = PMT × [1 - (1+r)^(-n)] / r
FV Annuity:             FV = PMT × [(1+r)^n - 1] / r
Perpetuity:             PV = PMT / r
Growing Perpetuity:     PV = PMT / (r - g)

──────────────────────────────────────────────────────────────────
BONDS
──────────────────────────────────────────────────────────────────
Bond Price:             P = Σ C/(1+r)^t + F/(1+r)^n
Modified Duration:      MD = Macaulay Duration / (1 + YTM/m)
Price Change:           ΔP/P ≈ -MD × Δy

──────────────────────────────────────────────────────────────────
EQUITY VALUATION
──────────────────────────────────────────────────────────────────
DDM (Gordon Growth):    P = D₁ / (r - g)
DCF:                    V = Σ FCF_t / (1+WACC)^t + TV/(1+WACC)^n
Terminal Value:         TV = FCF × (1+g) / (WACC - g)

──────────────────────────────────────────────────────────────────
PORTFOLIO THEORY
──────────────────────────────────────────────────────────────────
Portfolio Return:       Rp = Σ wᵢRᵢ
Portfolio Variance:     σ²p = w₁²σ₁² + w₂²σ₂² + 2w₁w₂ρσ₁σ₂
CAPM:                   E(Ri) = Rf + β × (Rm - Rf)
Alpha:                  α = Actual Return - CAPM Return
Sharpe Ratio:           (Rp - Rf) / σp

──────────────────────────────────────────────────────────────────
CORPORATE FINANCE
──────────────────────────────────────────────────────────────────
WACC:                   (E/V)×Re + (D/V)×Rd×(1-t)
MM (with tax):          VL = VU + t×D
NPV:                    Σ CF_t/(1+r)^t - Investment
Free Cash Flow:         FCF = Operating CF - CapEx

──────────────────────────────────────────────────────────────────
OPTIONS (BLACK-SCHOLES)
──────────────────────────────────────────────────────────────────
Call:                   C = S₀N(d₁) - Ke^(-rT)N(d₂)
Put:                    P = Ke^(-rT)N(-d₂) - S₀N(-d₁)
d₁ = [ln(S/K) + (r + σ²/2)T] / (σ√T)
d₂ = d₁ - σ√T

──────────────────────────────────────────────────────────────────
RISK
──────────────────────────────────────────────────────────────────
Parametric VaR:         Portfolio × z × σ × √T
Sharpe Ratio:           (Return - Rf) / StdDev
Sortino Ratio:          (Return - Rf) / Downside Deviation
Information Ratio:      Active Return / Tracking Error
──────────────────────────────────────────────────────────────────
```

---

## Glossary of Key Finance Terms

| Term              | Definition                                                    |
| ----------------- | ------------------------------------------------------------- |
| Alpha             | Excess return above benchmark (risk-adjusted)                 |
| Arbitrage         | Risk-free profit from price discrepancies                     |
| Asset Allocation  | Distribution of investments across asset classes              |
| Beta              | Sensitivity of asset return to market return                  |
| Bid-Ask Spread    | Difference between buy and sell price                         |
| Book Value        | Net asset value per share (Assets - Liabilities) / Shares     |
| Bull Market       | Sustained rise in asset prices (> 20% gain from trough)       |
| Bear Market       | Sustained fall in asset prices (> 20% decline from peak)      |
| CapEx             | Capital Expenditure — investment in long-term assets          |
| CAGR              | Compound Annual Growth Rate                                   |
| Correlation       | Statistical relationship between two variables (-1 to +1)     |
| Coupon            | Periodic interest payment on a bond                           |
| Default           | Failure to meet debt obligations                              |
| Deleveraging      | Reducing debt levels                                          |
| Derivative        | Contract whose value depends on an underlying asset           |
| Discount Rate     | Rate used to compute present value of future cash flows       |
| Diversification   | Spreading investments to reduce unsystematic risk             |
| Dividend          | Distribution of company profits to shareholders               |
| EBIT              | Earnings Before Interest and Taxes                            |
| EBITDA            | Earnings Before Interest, Taxes, Depreciation, Amortization   |
| Enterprise Value  | Market Cap + Debt - Cash                                      |
| EPS               | Earnings Per Share                                            |
| Equity            | Ownership stake in a company                                  |
| Fixed Income      | Debt instruments with predetermined cash flows                |
| Free Float        | Shares available for public trading (not held by insiders)    |
| Goodwill          | Premium paid in an acquisition above book value               |
| Hedge             | Position taken to reduce risk in another position             |
| IPO               | Initial Public Offering — first public sale of company shares |
| Leverage          | Using borrowed funds to amplify returns (and risk)            |
| Liquidity         | Ease of converting an asset to cash without price impact      |
| Margin of Safety  | Discount to intrinsic value; Benjamin Graham's principle      |
| Mark-to-Market    | Revaluing assets at current market prices                     |
| Maturity          | Date when bond principal is repaid                            |
| NAV               | Net Asset Value (total assets - liabilities) / units          |
| Par Value         | Face value of a bond or stock                                 |
| Portfolio         | Collection of investments held by an investor                 |
| Premium           | Price above face/par/intrinsic value                          |
| Short Selling     | Borrowing and selling an asset, hoping to buy back lower      |
| Spread            | Difference in yield between two bonds                         |
| Sunk Cost         | Past cost that cannot be recovered                            |
| Systematic Risk   | Market-wide risk (cannot be diversified)                      |
| Unsystematic Risk | Company-specific risk (can be diversified)                    |
| Volatility        | Measure of price fluctuation (standard deviation of returns)  |
| Working Capital   | Current Assets - Current Liabilities                          |
| Yield             | Return on investment (interest or dividend income / price)    |
| YTM               | Yield to Maturity — total return if bond held to maturity     |

---

**End of Document | Version 1.0 | Finance Reference Guide**
