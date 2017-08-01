var vue_delimiters = ['${', '}']; // Because Jinja2 already uses double brackets

Vue.component('itemsfilter', {
    delimiters: vue_delimiters,
    template: '#itemsfilter',
    props: ['items', 'recipe_item'],
    data: function() {
        return {
            query: ''
        };
    },
    computed: {
        filteredItems: function() {
            var filtered_items = {};

            for (var item_id in this.items) {
                var item = this.items[item_id];
                var match = true;

                if (this.query) {
                    match = (item.name.toLowerCase().indexOf(this.query.toLowerCase()) !== -1) || item.id == this.query;
                }

                if (match) {
                    filtered_items[item_id] = item;
                }
            }

            return filtered_items;
        }
    }
});

Vue.component('item', {
    delimiters: vue_delimiters,
    template: '#item',
    props: ['items', 'recipe_items', 'recipe_item']
});

var app = new Vue({
    delimiters: vue_delimiters,
    el: '#app',
    data: {
        loading: true,
        items: items,
        currentRecipe: current_recipe
    },
    mounted: function() {
        this.$nextTick(function () {
            this.loading = false;
        });
    },
    methods: {
        addItem: function(parent) {
            parent.push({
                id: '',
                amount: 1
            });
        },
        addOneOfGroup: function() {
            this.currentRecipe.items.push([]);
        }
    }
});