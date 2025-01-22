# **********************************************************************************************************************************************************************
# Part 1: Preparation
# - Imports / Data scources / basic style elements
# - run via: streamlit run main_nfl_app.py
# - Attention with appearance: 100% zoom in browser is optimal
# **********************************************************************************************************************************************************************
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from scipy.spatial import distance
from matplotlib.ticker import MaxNLocator

st.set_page_config(layout="wide")

# Data source 1: The unique combine data set
df_players_combine_unique = pd.read_csv('00_Data/players_unique_2010_2023.csv')

# Data source 2: The seasonal stats
df_season_data = pd.read_csv('00_Data/players_2010_2023.csv')

# Ensure the 'season' column is an integer and handle any invalid data
df_season_data['season'] = pd.to_numeric(df_season_data['season'], errors='coerce')

# Drop rows where 'season' is NaN or invalid
df_season_data = df_season_data.dropna(subset=['season'])
df_season_data['season'] = df_season_data['season'].astype(int)

sns.set_style("darkgrid")

# **********************************************************************************************************************************************************************
# Part 2: Conversion of values
# - only used for combine measurement values (easier to interpret in Europe).
# - KPIs for seasonal performance remain in the original unit
# **********************************************************************************************************************************************************************

# Conversion functions for player metrics for us in eu metrics
def feet_inches_to_cm(height):
    if isinstance(height, str) and '-' in height:
        feet, inches = height.split('-')
        return round((int(feet) * 12 + int(inches)) * 2.54, 2)
    return None

def pounds_to_kg(weight):
    return round(weight * 0.453592, 2) if pd.notnull(weight) else None

def inches_to_m(inches):
    return round(inches * 0.0254, 2) if pd.notnull(inches) else None

def inches_to_cm(inches):
    return round(inches * 2.54, 2) if pd.notnull(inches) else None

# Apply conversion functions to the relevant columns
df_players_combine_unique['Height_cm'] = df_players_combine_unique['Height'].apply(feet_inches_to_cm)
df_players_combine_unique['Weight_kg'] = df_players_combine_unique['Weight'].apply(pounds_to_kg)
df_players_combine_unique['BroadJump_m'] = df_players_combine_unique['Broad Jump'].apply(inches_to_m)
df_players_combine_unique['Vertical_cm'] = df_players_combine_unique['Vertical'].apply(inches_to_cm)

# **********************************************************************************************************************************************************************
# Part 3: Menu and UX/UI Design
# - pop-up window with additional information
# - sidebar main-menu
# - overall style of the dashboard
# - for the sources of used images see directly in css tags
# **********************************************************************************************************************************************************************

# Build up the menu and design
# Check if session state for pop-up exists, if not, set it to True so it shows the first time
if "popup_shown" not in st.session_state:
    st.session_state.popup_shown = False

# Function:display the help popup
def show_info_popup():
    st.session_state.popup_shown = True  # Ensure the pop-up is marked as shown in session state

    # pop-up content with an expander
    with st.expander("Welcome to the NFL Dashboard!"):
        st.markdown("""
        ## Welcome to the NFL Player Dashboard!
        This dashboard allows you to analyze and compare NFL players based on their combine data and seasonal performance metrics.

        ### Instructions:
        - **Analyze existing players:** Compare two players based on their combine and seasonal stats. To do this, select the desired position and the players to be compared in the menu on the right-hand side of the screen.
                    
        - **Record new players:** Add a new player, input their combine stats and get the most similar players of the NFL and their season performances.

        Use the **Help** button in the sidebar to reopen this information at any time.
        """)

# If the pop-up hasn't been shown yet, show it when the app is first loaded
if not st.session_state.popup_shown:
    show_info_popup()


# Add a help button to the sidebar to reopen the pop-up
if st.sidebar.button("Help"):
    show_info_popup()


# Sidebar radio selection for menu
menu_choice = st.sidebar.radio("Select Mode", ["Analyze existing players", "Record new players and compare performance"])

# Set up different titles, images, and explanations for each mode in CSS
if menu_choice == "Analyze existing players":
    headline = "Analyze existing players"
    image_url = "https://www.thewebfactory.us/blogs/wp-content/uploads/2022/09/NFL-LOGO-2.jpg"
    explanation = """
    You have selected the option to compare an existing player with other players. 
    Select the desired position and the players to be compared from the drop-down list
    """
    new_section_title = "Player Comparison - Combine data"
    new_section_explanation = """
    This section compares the Combine performance of the two players.
    """
    final_section_title = "Seasonal Data of both players"
    final_section_explanation = """
    Here you can get an insight into the season performances of the players
    """
elif menu_choice == "Record new players and compare performance":
    headline = "Record new players and compare their performance"
    image_url = "https://carolinablitz.com/wp-content/uploads/2024/02/NFL-Combine.jpeg"
    explanation = """
    You have selected the option to add a new player for comparison.
    Enter the player's position and metrics and then compare them with existing players.
    """
    new_section_title = "Compare Combine performance with existing players"
    new_section_explanation = """
    This section shows the top 10 most similar players based on the metrics entered for the new player and gives an overview on his combine performance.
    """
    final_section_title = "How would this player perform in a NFL season?"
    final_section_explanation = """
    To find out how players with similar Combine values have performed in the competition, select the desired players and metric
    """

# Display the headline, image, and info-box style explanation side by side
st.markdown(f"<h1 style='font-size: 40px;'>{headline}</h1>", unsafe_allow_html=True)

# Create two columns, one for the image, one for the explanation
col1, col2 = st.columns([1, 2])

# Left column: Image
with col1:
    st.image(image_url, width=300)  # Fixed size for the image

# Right column: Info-box styled explanation
with col2:
    st.markdown(
        f"""
        <div style='background-color: #f0f8ff; padding: 15px; border-radius: 10px; width: 100%;'>
            <img src="https://millingtonlibrary.info/wp-content/uploads/2015/02/Info-I-Logo.png" 
                 alt="info" 
                 style="width: 20px; height: 20px; position: absolute; top: 10px; right: 10px;">
            <p style='font-size: 18px; color: #555; margin-top: 10px;'>{explanation}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Add dividing line below the graphs
st.markdown("<hr>", unsafe_allow_html=True)

# New section with title and explanation below the graphs
st.markdown(f"<h2 style='font-size: 32px;'>{new_section_title}</h2>", unsafe_allow_html=True)

# Explanation for the new section, displayed in an info-box style
st.markdown(
    f"""
    <div style='background-color: #f0f8ff; padding: 15px; border-radius: 10px; width: 100%;'>
            <img src="https://millingtonlibrary.info/wp-content/uploads/2015/02/Info-I-Logo.png" 
                 alt="info" 
                 style="width: 20px; height: 20px; position: absolute; top: 10px; right: 10px;">
        <p style='font-size: 18px; color: #555; margin-top: 10px;'>{new_section_explanation}</p>
    </div>
    """, 
    unsafe_allow_html=True
)


# **********************************************************************************************************************************************************************
# Part 4: Combine for existing player
# - nested structure, depending on the selected menu, the corresponding page is displayed
# **********************************************************************************************************************************************************************

if menu_choice == "Analyze existing players":
    # Step 1: Select position first
    st.sidebar.subheader("Select Position")
    
    # Filter out NaN positions before showing in the selectbox
    valid_positions = df_players_combine_unique['Pos'].dropna().unique()
    selected_position = st.sidebar.selectbox("Select Position", valid_positions)

    # Filter data based on the selected position
    filtered_data = df_players_combine_unique[df_players_combine_unique['Pos'] == selected_position]

    # Step 2: Select two players from the selected position
    st.sidebar.subheader(f"Select two players playing in {selected_position}")
    player1 = st.sidebar.selectbox("Select Player 1", filtered_data['player_name'].unique())
    player2 = st.sidebar.selectbox("Select Player 2", filtered_data['player_name'].unique())

    # Display selected players' data
    if player1 and player2:
        st.subheader(f"Performance comparison between {player1} and {player2}")

        # Get player data for both players
        player1_data = filtered_data[filtered_data['player_name'] == player1]
        player2_data = filtered_data[filtered_data['player_name'] == player2]

        # Extract stats for player 1
        player1_position = player1_data['Pos'].values[0]
        player1_height = player1_data['Height_cm'].values[0]
        player1_weight = player1_data['Weight_kg'].values[0]
        player1_40yd = player1_data['40yd'].values[0]
        player1_vertical = player1_data['Vertical_cm'].values[0]
        player1_broad_jump = player1_data['BroadJump_m'].values[0]
        player1_bench = player1_data['Bench'].values[0]

        # Extract stats for player 2
        player2_position = player2_data['Pos'].values[0]
        player2_height = player2_data['Height_cm'].values[0]
        player2_weight = player2_data['Weight_kg'].values[0]
        player2_40yd = player2_data['40yd'].values[0]
        player2_vertical = player2_data['Vertical_cm'].values[0]
        player2_broad_jump = player2_data['BroadJump_m'].values[0]
        player2_bench = player2_data['Bench'].values[0]

        # Create DataFrame for the stats comparison, replacing NaN with "This value was not recorded" for error messages
        comparison_data = {
            "Metric": ["Position", "Height (cm)", "Weight (kg)", "40 Yard Dash (sec)", 
                    "Vertical Jump (cm)", "Broad Jump (m)", "Bench Press (reps)"],
            player1: [player1_position, player1_height, player1_weight, player1_40yd, 
                    player1_vertical, player1_broad_jump, player1_bench],
            player2: [player2_position, player2_height, player2_weight, player2_40yd, 
                    player2_vertical, player2_broad_jump, player2_bench]
        }

        comparison_df = pd.DataFrame(comparison_data).replace(np.nan, "This value was not recorded")

        # Display the DataFrame as a table without the index (index always visible...)
        st.table(comparison_df.set_index("Metric"))

        # Metrics to compare
        metrics = ['Height_cm', 'Weight_kg', '40yd', 'Vertical_cm', 'BroadJump_m', 'Bench']
        filtered_data = filtered_data.dropna(subset=metrics)

        # Error handling for missing metrics
        missing_metrics = [metric for metric in metrics if metric not in filtered_data.columns]
        if missing_metrics:
            st.error(f"The following columns are missing from the data: {', '.join(missing_metrics)}")
        elif filtered_data.empty:
            st.error("No data available for this position.")
        else:
            # Create a column for the plots (3x2 grid for each metric)
            for i in range(0, len(metrics), 3):
                cols = st.columns(3)  # Create 3 columns for the 3x2 grid

                for j, metric in enumerate(metrics[i:i+3]):
                    with cols[j]:
                        # Check values for both players and plot accordingly
                        player1_value = player1_data[metric].values[0]
                        player2_value = player2_data[metric].values[0]

                        if pd.notnull(player1_value) or pd.notnull(player2_value):
                            # Plot the boxplot and scatter both players' data points if at least one value is present
                            fig, ax = plt.subplots(figsize=(7, 5))
                            sns.boxplot(x='Pos', y=metric, data=filtered_data, ax=ax)

                            # Plot player 1's value if available
                            if pd.notnull(player1_value):
                                ax.scatter([0], [player1_value], color='red', s=100, zorder=5, label=player1)

                            # Plot player 2's value if available
                            if pd.notnull(player2_value):
                                ax.scatter([0], [player2_value], color='blue', s=100, zorder=5, label=player2)

                            # Set the legend to the upper right
                            ax.legend(loc="upper right")

                            ax.set_title(f'{metric} Comparison', fontsize=14)
                            ax.set_xlabel("Position", fontsize=12)
                            ax.set_ylabel(metric, fontsize=12)
                            st.pyplot(fig)
                        else:
                            # If both values are missing, show a message in a frame the same size as the plot
                            st.markdown(
                                f"""
                                <div style='border: 1px solid #ccc; padding: 20px; border-radius: 5px; height: 350px; display: flex; align-items: center; justify-content: center;'>
                                    <p style='color: #555;'>No data recorded for {metric} for either player.</p>
                                </div>
                                """, 
                                unsafe_allow_html=True)

        # Add dividing line below the graphs
        st.markdown("<hr>", unsafe_allow_html=True)

        # Initialize a list to store the warning messages
        warnings = []

        # Add Seasonal Performance plots for both players
        # Function to plot seasonal performance for the two players
        def plot_seasonal_performance(player1_name, player2_name, df_season_data):
            # Filter the data for the selected players
            filtered_data = df_season_data[df_season_data['player_name'].isin([player1_name, player2_name])]
    
            # Ensure each player is plotted for their active seasons only (2010-2023 is the valid range therefore)
            filtered_data = filtered_data[(filtered_data['season'] >= 2010) & (filtered_data['season'] <= 2023)]

            # Filter data for each player individually
            player1_data = filtered_data[filtered_data['player_name'] == player1_name]
            player2_data = filtered_data[filtered_data['player_name'] == player2_name]

            # warning messages
            warnings = []

            # Check if either or both players have no data and add warnings
            if player1_data.empty and player2_data.empty:
                warnings.append(f"For both {player1_name} and {player2_name}, no seasonal performance data is available.")
            elif player1_data.empty:
                warnings.append(f"For {player1_name}, no seasonal performance data is available.")
            elif player2_data.empty:
                warnings.append(f"For {player2_name}, no seasonal performance data is available.")

            # Dynamically update final_section_explanation to include warnings
            global final_section_explanation
            if warnings:
                # Append the warning messages to the explanation block
                warnings_text = "<br>".join(warnings)  # Join warnings with line breaks
                final_section_explanation += f"<br><strong>Warning:</strong><br>{warnings_text}"

            # Proceed only if there is data for at least one player
            if not player1_data.empty or not player2_data.empty:
                # Remove duplicates and NaN values for the selected metrics
                filtered_data = filtered_data.drop_duplicates(subset=['player_name', 'season', 'receiving_yards', 'receiving_tds', 'receptions', 'receiving_yards_after_catch'])
                filtered_data = filtered_data.dropna(subset=['receiving_yards', 'receiving_tds', 'receptions', 'receiving_yards_after_catch'])

                # Create a 2x2 grid of plots for the four metrics
                fig, axes = plt.subplots(2, 2, figsize=(14, 12))

                # Plot 1: Receiving Yards per season
                sns.lineplot(x='season', y='receiving_yards', hue='player_name', data=filtered_data, ax=axes[0, 0])
                axes[0, 0].set_title(f'Seasonal Receiving Yards Comparison')
                axes[0, 0].set_xlabel('Season')
                axes[0, 0].set_ylabel('Receiving Yards')
                axes[0, 0].xaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Force x-axis to show only integer years (2010 instead 2010.00)

                # Plot 2: Receiving Touchdowns per season
                sns.lineplot(x='season', y='receiving_tds', hue='player_name', data=filtered_data, ax=axes[0, 1])
                axes[0, 1].set_title(f'Seasonal Receiving TDs Comparison')
                axes[0, 1].set_xlabel('Season')
                axes[0, 1].set_ylabel('Receiving TDs')
                axes[0, 1].xaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Force x-axis to show only integer years

                # Plot 3: Catches (Receptions) per season
                sns.lineplot(x='season', y='receptions', hue='player_name', data=filtered_data, ax=axes[1, 0])
                axes[1, 0].set_title(f'Seasonal Catches (Receptions) Comparison')
                axes[1, 0].set_xlabel('Season')
                axes[1, 0].set_ylabel('Receptions')
                axes[1, 0].xaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Force x-axis to show only integer years

                # Plot 4: Yards after Catch per season
                sns.lineplot(x='season', y='receiving_yards_after_catch', hue='player_name', data=filtered_data, ax=axes[1, 1])
                axes[1, 1].set_title(f'Seasonal Yards after Catch Comparison')
                axes[1, 1].set_xlabel('Season')
                axes[1, 1].set_ylabel('Yards after Catch')
                axes[1, 1].xaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Force x-axis to show only integer years

                # Adjust layout and display the plots
                plt.tight_layout()
                st.pyplot(fig)

        if warnings:
            warnings_text = "<br>".join(warnings)  # Join warnings with line breaks
            final_section_explanation += f"<br><strong>Warning:</strong><br>{warnings_text}"

        # Display the title and explanation (including warnings if present)
        st.markdown(f"<h2>{final_section_title}</h2>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style='background-color: #f0f8ff; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                <p style='font-size: 18px; color: #333;'>{final_section_explanation}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

        # Plot the seasonal performance
        plot_seasonal_performance(player1, player2, df_season_data)


# **********************************************************************************************************************************************************************
# Part 3: Record a new player
# - Add Combine values of a new player in the side menu
# **********************************************************************************************************************************************************************

elif menu_choice == "Record new players and compare performance":

    # Use st.session_state to store the new player data and manage state
    if "compare_clicked" not in st.session_state:
        st.session_state.compare_clicked = False

    if "player_data" not in st.session_state:
        st.session_state.player_data = None

    # New player data entry
    selected_position = st.sidebar.selectbox("Position", ['WR', 'RB'], key="position_select")
    new_height = st.sidebar.number_input("Height (cm)", min_value=150.0, max_value=220.0, value=180.0, step=0.1, key="height_input")
    new_weight = st.sidebar.number_input("Weight (kg)", min_value=50.0, max_value=150.0, value=80.0, step=0.1, key="weight_input")
    new_40yd = st.sidebar.number_input("40 Yard Dash (sec)", min_value=4.0, max_value=6.0, value=4.5, step=0.1, key="40yd_input")
    new_vertical = st.sidebar.number_input("Vertical Jump (cm)", min_value=50.0, max_value=120.0, value=80.0, step=0.1, key="vertical_input")
    new_broad_jump = st.sidebar.number_input("Broad Jump (m)", min_value=2.0, max_value=4.0, value=3.0, step=0.01, key="broad_jump_input")
    new_bench = st.sidebar.number_input("Bench Press (count)", min_value=0, max_value=50, value=20, step=1, key="bench_input")

    # Store the new player's data in session_state
    st.session_state.player_data = {
        'Height_cm': new_height,
        'Weight_kg': new_weight,
        '40yd': new_40yd,
        'Vertical_cm': new_vertical,
        'BroadJump_m': new_broad_jump,
        'Bench': new_bench
    }

    # Button to trigger the comparison
    if st.sidebar.button("Compare"):
        st.session_state.compare_clicked = True

    # If compare button is clicked, calculate and display the comparison
    if st.session_state.compare_clicked and st.session_state.player_data:
        new_player_data = st.session_state.player_data

        # Filter players by the selected position
        filtered_data = df_players_combine_unique[df_players_combine_unique['Pos'] == selected_position]

        # Create two columns, left for the player values and right for the similar players
        col1, col2 = st.columns([1, 1])  # Ensure both columns take equal space for the layout

        # Left column: Display entered player values
        with col1:
            # Add title for entered player values
            st.markdown("<h3>Entered Player Values</h3>", unsafe_allow_html=True)

            # Style the entered values for better spacing with margin between elements
            st.markdown(f"""
            <div style='line-height: 2; margin-bottom: 1em;'>  <!-- Line height and margin adjusted for better spacing -->
                <p style='margin-bottom: 20px;'>- <strong>Selected Position</strong>: {selected_position}</p>
                <p style='margin-bottom: 20px;'>- <strong>Height</strong>: {new_height} cm</p>
                <p style='margin-bottom: 20px;'>- <strong>Weight</strong>: {new_weight} kg</p>
                <p style='margin-bottom: 20px;'>- <strong>40 Yard Dash</strong>: {new_40yd} sec</p>
                <p style='margin-bottom: 20px;'>- <strong>Vertical Jump</strong>: {new_vertical} cm</p>
                <p style='margin-bottom: 20px;'>- <strong>Broad Jump</strong>: {new_broad_jump} m</p>
                <p style='margin-bottom: 20px;'>- <strong>Bench Press</strong>: {new_bench} reps</p>
            </div>
            """, unsafe_allow_html=True)

        # Right column: Show the top 10 similar players
        # *****************************************************************************************************************
        # How does it work:
        # - First the values (existing and newly added) are scaled (reason: different metrics)
        # - Function calculates the Euclidean distance between the new player and every other player
        #   - Only players with the same position as the new player are compared
        # - Sort the data based on distance
        # *****************************************************************************************************************
        with col2:
            def find_similar_players(new_player_data, filtered_data, metrics, n=10):
                filtered_metrics = filtered_data[metrics]
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(filtered_metrics)
                new_player_df = pd.DataFrame([new_player_data], columns=metrics)
                scaled_new_player = scaler.transform(new_player_df)
                distances = distance.cdist(scaled_new_player, scaled_data, 'euclidean').flatten()
                filtered_data.loc[:, 'Distance'] = distances
                similar_players = filtered_data.sort_values(by='Distance').head(n).reset_index(drop=True)
                similar_players.insert(0, 'Rank', range(1, len(similar_players) + 1))
                return similar_players

            # Define the metrics to compare
            metrics = ['Height_cm', 'Weight_kg', '40yd', 'Vertical_cm', 'BroadJump_m', 'Bench']
            
            similar_players = find_similar_players(new_player_data, filtered_data, metrics, n=10)

            # Add title and show the table of similar players
            st.markdown("<h3>Top 10 Similar Players</h3>", unsafe_allow_html=True)
            st.dataframe(similar_players[['Rank', 'player_name']])

        # *** Seasonal Performance Plot ***
        st.markdown("<hr>", unsafe_allow_html=True)
        # Display the title and explanation (including warnings if present)
        st.markdown(f"<h2>{final_section_title}</h2>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style='background-color: #f0f8ff; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                <p style='font-size: 18px; color: #333;'>{final_section_explanation}</p>
            </div>
            """, 
            unsafe_allow_html=True)

        player_list = similar_players['player_name'].tolist()
        selected_players = st.multiselect("Select players to view seasonal performance", player_list, default=player_list[:1])

        # Create a dropdown to select the seasonal indicator (depending on position)
        if selected_position == 'WR':
            seasonal_stat = st.selectbox("Select a performance metric", 
                                        ['receiving_yards', 'receiving_tds', 'receiving_yards_after_catch', 'receptions'])
        elif selected_position == 'RB':
            seasonal_stat = st.selectbox("Select a performance metric", 
                                        ['carries', 'rushing_yards', 'rushing_tds'])

        # Only update the graph when players are selected and a new seasonal stat is chosen
        if selected_players and seasonal_stat:
            st.subheader(f"Seasonal Performance for Selected Players - {seasonal_stat.replace('_', ' ').title()}")

            # Filter the seasonal data for the selected players and seasons (2010-2023)
            filtered_season_data = df_season_data[
                (df_season_data['player_name'].isin(selected_players)) &
                (df_season_data['season'] >= 2010) & 
                (df_season_data['season'] <= 2023)]

            # Remove duplicate rows for the same player, season, and selected metric
            filtered_season_data = filtered_season_data.drop_duplicates(subset=['player_name', 'season', seasonal_stat])

            # Remove rows with NaN values in the selected stat column
            filtered_season_data = filtered_season_data.dropna(subset=[seasonal_stat])

            # Calculate the mean of the selected metric for all players in the same position
            position_mean_per_year = df_season_data[
                (df_season_data['position'] == selected_position) & 
                (df_season_data['season'] >= 2010) & 
                (df_season_data['season'] <= 2023)
            ].groupby('season')[seasonal_stat].mean().reset_index()

            # Ensure seasonal_stat exists in the data
            if seasonal_stat in filtered_season_data.columns:
                # Create a line plot for the seasonal performance of the selected players
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.lineplot(x='season', y=seasonal_stat, hue='player_name', data=filtered_season_data, ax=ax)

                # Plot the yearly mean values for the selected position
                sns.lineplot(x='season', y=seasonal_stat, data=position_mean_per_year, ax=ax, color='gray', linestyle='--', label=f'Mean {seasonal_stat.replace("_", " ").title()} for {selected_position}')

                ax.set_title(f'Seasonal {seasonal_stat.replace("_", " ").title()} Performance', fontsize=16)
                ax.set_xlabel('Season', fontsize=14)
                ax.set_ylabel(seasonal_stat.replace('_', ' ').title(), fontsize=14)
                ax.legend()
                st.pyplot(fig)
            else:
                st.write(f"No data available for {seasonal_stat}.")

# Add a dividing line at the end of the dashboard page
st.markdown("<hr>", unsafe_allow_html=True)

# **********************************************************************************************************************************************************************
# Part 4: Final section
# **********************************************************************************************************************************************************************

# Quick note with Authors information
st.markdown(
    """
    <div style='text-align: center; color: #777; padding-top: 10px; font-size: 14px;'>
        <em>This dashboard is part of a student project of the Lucerne University of Applied Science of the Applied Information and Data Science program. 
        \n Authors: Viktor Huber & Carlo Scherrer </em>
    </div>
    """, 
    unsafe_allow_html=True)

# **********************************************************************************************************************************************************************
# Have fun testing it out! :) Viktor & Carlo








