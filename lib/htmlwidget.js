import * as mc from "@uwdata/mosaic-core";
import * as msql from "@uwdata/mosaic-sql";

import { datatable } from "./clients/DataTable.ts";

export default () => {
	let tableName = "df";
	let coordinator;
	let options;

	return {
		async initialize(options) {
		  let exec;

		  if(coordinator) {
		    // already initialized
		  } else {
		    options = options;
        coordinator = new mc.Coordinator();
      	let connector = mc.wasmConnector();
      	let db = await connector.getDuckDB();
      	coordinator.databaseConnector(connector);
  			const res = await fetch(options.file.url);
        await db.registerFileBuffer(options.file.name, new Uint8Array(await res.arrayBuffer()));
  			exec = msql.loadParquet(tableName, options.file.name, { replace: true });

      	await coordinator.exec([exec]);
		  }
		},
		async render(el) {
    	let dt = await datatable(tableName, { coordinator, height: 500 });
			el.appendChild(dt.node());
		},
	};
};
