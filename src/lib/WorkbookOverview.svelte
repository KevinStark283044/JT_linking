<script lang="ts">
    import { onMount } from "svelte";
  
    let selectedScenario: string = "";
    let selectedCategory: string = "";
    let results: Array<{ value1: string; value2: string }> = [];
    let errorMessage: string = "";
  
    // Fetch data function
    async function fetchData() {
      if (!selectedScenario || !selectedCategory) {
        errorMessage = "Please select both a scenario and a category.";
        return;
      }
  
      try {
        const response = await fetch("http://127.0.0.1:5000/codes/content/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ selectedScenario, selectedCategory }),
        });
  
        if (!response.ok) {
          throw new Error("Failed to fetch data from the server.");
        }
  
        const data = await response.json();
        results = data.results || [];
        errorMessage = results.length === 0 ? "No results found." : "";
      } catch (error) {
        console.error(error);
        errorMessage = "An error occurred while fetching data.";
      }
    }
  </script>
  
  <style>
    .flex {
      display: flex;
    }
    .flex-col {
      flex-direction: column;
    }
    .gap-y-2 > * + * {
      margin-top: 8px;
    }
    .gap-x-4 > * + * {
      margin-left: 16px;
    }
    select,
    button {
      padding: 5px;
      font-size: 1em;
    }
    .results {
      margin-top: 20px;
      padding: 10px;
      border: 1px solid #ccc;
      background: #f9f9f9;
    }
    .error {
      color: red;
      font-weight: bold;
      margin-top: 10px;
    }
  </style>
  
  <div class="flex flex-col gap-y-2">
    <div class="flex gap-x-4">
      <select bind:value={selectedScenario}>
        <option value="" disabled selected>Select Scenario</option>
        <option value="BUSINESS AS USUAL">BUSINESS AS USUAL</option>
        <option value="ECO MACHINE">ECO MACHINE</option>
        <option value="CALLING ON RESERVES">CALLING ON RESERVES</option>
        <option value="TUNNEL VISION">TUNNEL VISION</option>
        <option value="NEW GREEN WATERSHED">NEW GREEN WATERSHED</option>
        <option value="BOLSTER & FORTIFY">BOLSTER & FORTIFY</option>
      </select>
      <select bind:value={selectedCategory}>
        <option value="" disabled selected>Select Category</option>
        <option value="BENEFITS MAJORS">BENEFITS MAJORS</option>
        <option value="BENEFITS NEUTRAL">BENEFITS NEUTRAL</option>
        <option value="BENEFITS MINOR">BENEFITS MINOR</option>
        <option value="NEUTRAL MAJOR">NEUTRAL MAJOR</option>
        <option value="NEUTRAL NEUTRAL">NEUTRAL NEUTRAL</option>
        <option value="NEUTRAL MINOR">NEUTRAL MINOR</option>
        <option value="IMPACTS MAJORS">IMPACTS MAJORS</option>
        <option value="IMPACTS NEUTRAL">IMPACTS NEUTRAL</option>
        <option value="IMPACTS MINOR">IMPACTS MINOR</option>
      </select>
      <button on:click={fetchData}>Search</button>
    </div>
    <div>
      {selectedScenario || "Not Selected"} - {selectedCategory || "Not Selected"}
    </div>
    {#if errorMessage}
      <div class="error">{errorMessage}</div>
    {/if}
  </div>
  
  {#if results.length > 0}
    <div class="results">
      <h3>Results</h3>
      <ul>
        {#each results as { value1, value2 }}
          <li>{value1} - {value2}</li>
        {/each}
      </ul>
    </div>
  {/if}
  