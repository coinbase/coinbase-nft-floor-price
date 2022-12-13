# Coinbase NFT Floor Price Estimate

This repository contains the core functions used in Coinbase's NFT floor price estimate model. The model gives an estimate of the current floor price for a given NFT collection based on trading prices; note that this approach differs from the common way of calculating the floor price based on listed prices. To help understand the context for these functions, we also provide some sample data on NFT trades and a script that illustrates how these functions are applied to these data. 

The intention for this repository is for someone with a reasonably up-to-date personal computer to be able to run these functions and produce the NFT floor price estimates. As such, in our example script, we leverage the widely available functionality from the [pandas](https://pandas.pydata.org/) library. In production, we have used the same core functions to be able to calculate in somewhat real-time fashion the NFT floor price estimates for more than 10,000 collections.

## Description of the files in the repository

* ``cbnftfloorprice.py``, the core functions for the NFT floor price estimate
* ``CONTRIBUTING.md``, how to contribute to the repository
* ``LICENSE.md``, the open-source license
* ``nft_trades.csv``, file containing sample data, see below
* ``README.md``, this file
* ``requirements.txt``, required Python packages to run the code
* ``run_cbnftfloorprice.py``, script to run the NFT floor price estimate calculation for the given sample data

## Model

We describe a method that can estimate the floor price price quickly and accurately for over 30,000 NFT collections on the mainnet with an average SLA of 15 minutes for freshness. The method is called the adaptive percentile predictor, as it aims to adaptively predict the next moment floor price level below which only X% of the transactions should land. 

Traditional methodology tries to set a fixed percentile on a historical period of data to predict such a floor price level for the future. This approach is rigid and inaccurate, as the true empirical performance could deviate away from the X% target due to the changing data patterns. 

Instead of using a rigid and fixed percentile, an adaptive percentile approach was chosen where the used percentile parameter will be adjusted according to the observed error rate from time to time. This kind of dynamic control will make sure the overall error rate is small and the X% percentile target can be reached. Put it another way, it is similar to the temperature control system of the air conditioning unit, where it automatically turns on or off the engine when the temperature is above or below a certain range centered around the user preference.

The overall algorithm can be summarized in four abstract steps:

* Remove extreme outliers from the transaction data stream
* Continuously estimate the floor price as new data shows up using the current percentile parameter Z% 
* Once a while, perform a backtesting for a longer period in the past, and calculate the percentage of data (Y%) below our floor prices
* If the backtesting shows Y% == X%, do nothing; Otherwise, feed the error (Y-X)% back to adjust the parameter Z%

The details of the algorithm can be found in the source code of this repo.

## Sample data

In ``nft_trades.csv``, we provide trade data until 2022-10-31 23:59:59 UTC of the following collections on Ethereum mainnet:
* [Azuki](https://nft.coinbase.com/collection/ethereum/0xed5af388653567af2f388e6224dc7c4b3241c544) (contract address [0xed5af388653567af2f388e6224dc7c4b3241c544](https://etherscan.io/address/0xed5af388653567af2f388e6224dc7c4b3241c544))
* [Bored Ape Yacht Club](https://nft.coinbase.com/collection/ethereum/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d) (contract address [0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d](https://etherscan.io/address/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d))
* [Doodles](https://nft.coinbase.com/collection/ethereum/0x8a90cab2b38dba80c64b7734e58ee1db38b8992e) (contract address [0x8a90cab2b38dba80c64b7734e58ee1db38b8992e](https://etherscan.io/address/0x8a90cab2b38dba80c64b7734e58ee1db38b8992e))

## How to run

Prerequisites: Python 3.7+.

* Clone the repo

* Install the required packages: `pip install -r requirements.txt`

* Running the example: `python run_cbnftfloorprice.py`
