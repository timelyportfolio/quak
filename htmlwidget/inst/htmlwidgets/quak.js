HTMLWidgets.widget({

  name: 'quak',

  type: 'output',

  factory: function(el, width, height) {

    // TODO: define shared variables for this instance

    return {

      renderValue: async function(x) {

        const q = quak.default();
        const options = {
          file:{
            url: document.getElementById(`${x.name}-1-attachment`).href,
            name: x.name
          }
        }

        await q.initialize(options);
        await q.render(el);

      },

      resize: function(width, height) {

        // TODO: code to re-render the widget with a new size

      }

    };
  }
});
