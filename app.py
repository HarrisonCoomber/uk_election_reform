import pandas
import matplotlib.pyplot as plt
import geopandas
from pathlib import Path
from shiny import reactive
from shiny.ui import sidebar
from shiny.express import input, render, ui

def dat():
    infile = Path(__file__).parent / "data/processed_data/ge_2019_data.shp"
    return geopandas.read_file(infile)
# return dataframe

def hex_dat():
    infile = Path(__file__).parent / "data/processed_data/ge_2019_hex_data.shp"
    return geopandas.read_file(infile)
# return dataframe

df = dat()
hex_df = hex_dat()

colour_map = {"Lab":"red",
              "Con":"blue",
              "SNP":"gold",
              "LD":"orange",
              "PC":"darkolivegreen",
              "BRX":"teal",
              "Green":"green",
              "DUP":"purple",
              "SF":"purple",
              "SDLP":"purple",
              "Spk":"purple",
              "APNI":"purple",
              "Other":"grey",
              }

parties = [
    "Con",
    "Lab",
    "LD",
    "BRX",
    "Green",
    "PC",
    "SNP",
    'Other',
    ]

def nav_controls(prefix: str) -> List[NavSetArg]:
    return [
        ui.nav_panel("a", prefix + ": tab a content"),
        ui.nav_panel("b", prefix + ": tab b content"),
    ]


ui.page_opts(
    title = "General Election 2019 Vote Swings",
    fillable=True,
    # page_fn=partial(page_navbar, id="page")
    )

navset_sidebar = sidebar(
    ui.input_slider(
        "swing", 
        "Swing vote percentage",
        -100, 
        100, 
        0
    ),
    
    # Input: Selector for choosing dataset ----
    ui.input_selectize(
        id = "from_party",
        label = "Party A",
        choices = parties
    ),

    # Input: Selector for choosing dataset ----
    ui.input_selectize(
        id = "to_party",
        label = "Party B",
        choices = parties
    )

)



with ui.navset_card_tab(sidebar=navset_sidebar):
    with ui.nav_panel("UK Geographic Plot"):

        @render.plot
        def geo_plot():
            
            # swing from {from_party} to {to_party}
            from_party = input.from_party()
            to_party = input.to_party()

            for party in parties:
                df[f"{party}_prop_new"] = df[f"{party}_prop"].copy()
                    
            if from_party != to_party:

                # positive swings from {from_party} to {to_party}
                df.loc[(df[f"{from_party}_prop"] >= (input.swing()/2)) &
                    (input.swing()>=0),
                    f"{from_party}_prop_new"] = round( (df[f"{from_party}_prop"] - (input.swing()/2)), 2)
                df.loc[(df[f"{from_party}_prop"] >= (input.swing()/2)) &
                    (input.swing()>=0),
                    f"{to_party}_prop_new"] = round( (df[f"{to_party}_prop"] + (input.swing()/2)), 2)

                df.loc[(df[f"{from_party}_prop"] < (input.swing()/2)) &
                    (input.swing()>=0),
                    f"{from_party}_prop_new"] = 0
                df.loc[(df[f"{from_party}_prop"] < (input.swing()/2)) &
                    (input.swing()>=0),
                    f"{to_party}_prop_new"] = round( (df[f"{from_party}_prop"] + df[f"{to_party}_prop"]), 2)

                # Negative swings: Postive from {to_party} to {from_party}
                # watch for switch of ( +/- sign due to negative swing value)
                df.loc[(df[f"{to_party}_prop"] >= (abs(input.swing()/2))) &
                    (input.swing()<0),
                    f"{from_party}_prop_new"] = round( (df[f"{from_party}_prop"] - (input.swing()/2)), 2)
                df.loc[(df[f"{to_party}_prop"] >= (abs(input.swing()/2))) &
                    (input.swing()<0),
                    f"{to_party}_prop_new"] = round( (df[f"{to_party}_prop"] + (input.swing()/2)), 2)

                df.loc[(df[f"{to_party}_prop"] < (abs(input.swing()/2))) &
                    (input.swing()<0),
                    f"{to_party}_prop_new"] = 0
                df.loc[(df[f"{to_party}_prop"] < (abs(input.swing()/2))) &
                    (input.swing()<0),
                    f"{from_party}_prop_new"] = round( (df[f"{to_party}_prop"] + df[f"{from_party}_prop"]), 2)

            # Creating a new column based on multiple conditions
            df["new_party"] = [
                "Con" if a > max(b, c, d, e, f, g, h) else
                "Lab" if b > max(a, c, d, e, f, g, h) else
                "LD" if c > max(a, b, d, e, f, g, h) else
                "BRX" if d > max(a, b, c, e, f, g, h) else
                "Green" if e > max(a, b, c, d, f, g, h) else
                "PC" if f > max(a, b, c, d, e, g, h) else
                "SNP" if g > max(a, b, c, d, e, f, h) else
                "Other"
                for a, b, c, d, e, f, g, h in zip(df["Con_prop_new"],
                                                df["Lab_prop_new"],
                                                df["LD_prop_new"],
                                                df["BRX_prop_new"],
                                                df["Green_prop_new"],
                                                df["PC_prop_new"],
                                                df["SNP_prop_new"],
                                                df["Other_prop_new"]
                                                )
            ]

            fig, ax = plt.subplots(figsize=(10,6))

            df.plot(ax=ax, 
                color=df["new_party"].map(colour_map)
                )

            # Set custom y range
            ax.set_ylim(0, 0.98e+06)  # Set y-axis range from 0 to 50

            # Remove axis, ticks, tick values, and border
            ax.axis('off')  # Remove the axis
            ax.set_xticks([])  # Remove x-axis ticks
            ax.set_yticks([])  # Remove y-axis ticks
            ax.xaxis.set_ticklabels([])  # Remove x-axis tick labels
            ax.yaxis.set_ticklabels([])  # Remove y-axis tick labels
            ax.spines['top'].set_visible(False)  # Remove the top spine
            ax.spines['right'].set_visible(False)  # Remove the right spine
            ax.spines['left'].set_visible(False)  # Remove the left spine
            ax.spines['bottom'].set_visible(False)  # Remove the bottom spine

            return fig

    with ui.nav_panel("UK Hexagonal Plot"):
        @render.plot
        def hex_plot():
            
            # swing from {from_party} to {to_party}
            from_party = input.from_party()
            to_party = input.to_party()

            for party in parties:
                hex_df[f"{party}_prop_new"] = hex_df[f"{party}_prop"].copy()
                    
            if from_party != to_party:

                # positive swings from {from_party} to {to_party}
                hex_df.loc[(hex_df[f"{from_party}_prop"] >= (input.swing()/2)) &
                    (input.swing()>=0),
                    f"{from_party}_prop_new"] = round( (hex_df[f"{from_party}_prop"] - (input.swing()/2)), 2)
                hex_df.loc[(hex_df[f"{from_party}_prop"] >= (input.swing()/2)) &
                    (input.swing()>=0),
                    f"{to_party}_prop_new"] = round( (hex_df[f"{to_party}_prop"] + (input.swing()/2)), 2)

                hex_df.loc[(hex_df[f"{from_party}_prop"] < (input.swing()/2)) &
                    (input.swing()>=0),
                    f"{from_party}_prop_new"] = 0
                hex_df.loc[(hex_df[f"{from_party}_prop"] < (input.swing()/2)) &
                    (input.swing()>=0),
                    f"{to_party}_prop_new"] = round( (hex_df[f"{from_party}_prop"] + hex_df[f"{to_party}_prop"]), 2)

                # Negative swings: Postive from {to_party} to {from_party}
                # watch for switch of ( +/- sign due to negative swing value)
                hex_df.loc[(hex_df[f"{to_party}_prop"] >= (abs(input.swing()/2))) &
                    (input.swing()<0),
                    f"{from_party}_prop_new"] = round( (hex_df[f"{from_party}_prop"] - (input.swing()/2)), 2)
                hex_df.loc[(hex_df[f"{to_party}_prop"] >= (abs(input.swing()/2))) &
                    (input.swing()<0),
                    f"{to_party}_prop_new"] = round( (hex_df[f"{to_party}_prop"] + (input.swing()/2)), 2)

                hex_df.loc[(hex_df[f"{to_party}_prop"] < (abs(input.swing()/2))) &
                    (input.swing()<0),
                    f"{to_party}_prop_new"] = 0
                hex_df.loc[(hex_df[f"{to_party}_prop"] < (abs(input.swing()/2))) &
                    (input.swing()<0),
                    f"{from_party}_prop_new"] = round( (hex_df[f"{to_party}_prop"] + hex_df[f"{from_party}_prop"]), 2)

            # Creating a new column based on multiple conditions
            hex_df["new_party"] = [
                "Con" if a > max(b, c, d, e, f, g, h) else
                "Lab" if b > max(a, c, d, e, f, g, h) else
                "LD" if c > max(a, b, d, e, f, g, h) else
                "BRX" if d > max(a, b, c, e, f, g, h) else
                "Green" if e > max(a, b, c, d, f, g, h) else
                "PC" if f > max(a, b, c, d, e, g, h) else
                "SNP" if g > max(a, b, c, d, e, f, h) else
                "Other"
                for a, b, c, d, e, f, g, h in zip(hex_df["Con_prop_new"],
                                                hex_df["Lab_prop_new"],
                                                hex_df["LD_prop_new"],
                                                hex_df["BRX_prop_new"],
                                                hex_df["Green_prop_new"],
                                                hex_df["PC_prop_new"],
                                                hex_df["SNP_prop_new"],
                                                hex_df["Other_prop_new"]
                                                )
            ]

            fig, ax = plt.subplots(figsize=(10,6))

            hex_df.plot(ax=ax, 
                color=hex_df["new_party"].map(colour_map)
                )

            # Remove axis, ticks, tick values, and border
            ax.axis('off')  # Remove the axis
            ax.set_xticks([])  # Remove x-axis ticks
            ax.set_yticks([])  # Remove y-axis ticks
            ax.xaxis.set_ticklabels([])  # Remove x-axis tick labels
            ax.yaxis.set_ticklabels([])  # Remove y-axis tick labels
            ax.spines['top'].set_visible(False)  # Remove the top spine
            ax.spines['right'].set_visible(False)  # Remove the right spine
            ax.spines['left'].set_visible(False)  # Remove the left spine
            ax.spines['bottom'].set_visible(False)  # Remove the bottom spine

            return fig            