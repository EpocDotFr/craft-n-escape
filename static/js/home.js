var vue_delimiters = ['${', '}']; // Because Jinja2 already uses double brackets

Vue.component('recipeitem', {
    delimiters: vue_delimiters,
    template: '#recipeitem',
    props: ['items', 'recipe_item', 'escapistswikisearch']
});

Vue.component('itemname', {
    delimiters: vue_delimiters,
    template: '#itemname',
    props: ['item', 'itemid', 'escapistswikisearch']
});

Vue.component('itemiownform', {
    delimiters: vue_delimiters,
    template: '#itemiownform',
    props: ['items', 'items_i_own'],
    data: function() {
        return {
            query: '',
            addItem: {
                id: '',
                amount: 1,
            }
        };
    },
    computed: {
        filteredItems: function() {
            var filtered_items = {};

            _.each(this.items, function(item, item_id) {
                var match = true;

                if (this.query) {
                    match = (item.name.toLowerCase().indexOf(this.query.toLowerCase()) !== -1);
                }

                if (match) {
                    filtered_items[item_id] = item;
                }
            }, this);

            return filtered_items;
        }
    },
    methods: {
        addItemIOwn: function() {
            // If the item to add is already present in the items I own list, just increment its amount
            var already_present = _.findIndex(this.items_i_own, function(itemIOwn) {
                return itemIOwn.id == this.addItem.id;
            }, this);

            if (already_present == -1) {
                this.items_i_own.push({
                    id: this.addItem.id,
                    amount: this.addItem.amount
                });
            } else {
                this.items_i_own[already_present].amount += this.addItem.amount;
            }

            this.query = '';
            this.addItem.id = '';
            this.addItem.amount = 1;
        }
    }
});

var app = new Vue({
    delimiters: vue_delimiters,
    el: '#app',
    data: {
        loading: true,
        items: items,
        escapistsWikiSearch: 'http://' + ESCAPISTS_WIKI_DOMAIN + '/Special:Search/',
        filters: {
            name: '',
            found_in_map: '',
            is_buyable: false,
            can_heal: false,
            can_hurt: false,
            can_dig: false,
            can_chop: false,
            can_unscrew: false,
            can_cut: false,
            is_carried: false,
            is_in_desks: false,
            can_disrupt_cameras: false,
            is_outfit: false,
            is_craftable: false,
            is_illegal: false
        },
        itemsIOwn: [],
        maps: {
            'irongate': 'HMP-Irongate',
            'perks': 'Center Perks',
            'jungle': 'Jungle Compound',
            'stalagflucht': 'Stalag Flucht',
            'sanpancho': 'San Pancho',
            'escapeteam': 'Escape Team',
            'DTAF': 'Duct Tapes Are Forever',
            'SS': 'Santa\'s Sweatshop'
        }
    },
    mounted: function() {
        this.$nextTick(function () {
            this.loading = false;
        });
    },
    computed: {
        componentItems: function() {
            var component_items = {};

            _.each(this.items, function(item, item_id) {
                if (('craft' in item)) {
                    _.each(_.flatten(item.craft.recipe_items), function(recipe_item) { // We don't care making the difference between a recipe item and a One of group
                        if (!(recipe_item.id in component_items)) {
                            component_items[recipe_item.id] = this.items[recipe_item.id];
                        }
                    }, this);
                }
            }, this);

            return component_items;
        },
        itemIdsICanCraft: function() {
            var item_ids_i_can_craft = [];

            if (!_.isEmpty(this.itemsIOwn)) {
                _.each(this.items, function(item, item_id) { // For each available items
                    // First make sure this item:
                    //   - Has a crafting recipe
                    //   - Hasn't been added yet to our items I can craft list
                    if (('craft' in item) && item_ids_i_can_craft.indexOf(item_id) === -1) {
                        var valid_items_count = 0;

                        // Check if I own all the items at least one time each, and at least one of the One of groups
                        _.find(this.itemsIOwn, function(itemIOwn) {
                            _.find(item.craft.recipe_items, function(recipe_item) {
                                if (_.isArray(recipe_item)) { // One of those recipe items are required, so break when we found one
                                    _.find(recipe_item, function(one_of_recipe_item) {
                                        if (itemIOwn.id == one_of_recipe_item.id && itemIOwn.amount >= one_of_recipe_item.amount) {
                                            valid_items_count++;
                                            return true;
                                        }

                                        return false;
                                    }, this);
                                } else { // If the item in the recipe items list is present, its is required
                                    if (itemIOwn.id == recipe_item.id && itemIOwn.amount >= recipe_item.amount) {
                                        valid_items_count++;
                                        return true;
                                    }

                                    return false;
                                }
                            }, this);
                        }, this);

                        // If all items I own are valid components to craft this item
                        if (valid_items_count == item.craft.recipe_items.length) {
                            item_ids_i_can_craft.push(item_id);
                        }
                    }
                }, this);
            }

            return item_ids_i_can_craft;
        },
        filteredItems: function () {
            var filtered_items = {};

            _.each(this.items, function(item, item_id) {
                var name = found_in_map = is_buyable = can_heal = can_hurt = can_dig = can_chop = can_unscrew = can_cut = is_carried = is_in_desks = can_disrupt_cameras = is_outfit = is_craftable = is_illegal = can_i_craft = true;

                if (('name' in item) && this.filters.name) {
                    name = item.name.toLowerCase().indexOf(this.filters.name.toLowerCase()) !== -1;
                }

                if (this.filters.found_in_map) {
                    found_in_map = ('found' in item) && item.found == this.filters.found_in_map;
                }

                if (this.filters.is_buyable) {
                    is_buyable = ('buy' in item);
                }

                if (this.filters.can_heal) {
                    can_heal = ('hp' in item);
                }

                if (this.filters.can_hurt) {
                    can_hurt = ('weapon' in item);
                }

                if (this.filters.can_dig) {
                    can_dig = ('digging' in item);
                }

                if (this.filters.can_chop) {
                    can_chop = ('chipping' in item);
                }

                if (this.filters.can_unscrew) {
                    can_unscrew = ('unscrewing' in item);
                }

                if (this.filters.can_cut) {
                    can_cut = ('cutting' in item);
                }

                if (this.filters.is_carried) {
                    is_carried = ('npc_carry' in item);
                }

                if (this.filters.is_in_desks) {
                    is_in_desks = ('desk' in item);
                }

                if (this.filters.can_disrupt_cameras) {
                    can_disrupt_cameras = ('camdis' in item);
                }

                if (this.filters.is_outfit) {
                    is_outfit = ('outfit' in item);
                }

                if (this.filters.is_illegal) {
                    is_illegal = ('illegal' in item);
                }

                if (!_.isEmpty(this.itemsIOwn)) {
                    can_i_craft = this.itemIdsICanCraft.indexOf(item_id) !== -1;
                } else if (this.filters.is_craftable) {
                    is_craftable = ('craft' in item);
                }

                if (name && found_in_map && is_buyable && can_heal && can_hurt && can_dig && can_chop && can_unscrew && can_cut && is_carried && is_in_desks && can_disrupt_cameras && is_outfit && is_craftable && is_illegal && can_i_craft) {
                    filtered_items[item_id] = item;
                }
            }, this);

            return filtered_items;
        }
    },
    methods: {
        clearAllFilters: function() {
            this.filters.name = '';
            this.filters.found_in_map = '';
            this.filters.is_buyable = false;
            this.filters.can_heal = false;
            this.filters.can_hurt = false;
            this.filters.can_dig = false;
            this.filters.can_chop = false;
            this.filters.can_unscrew = false;
            this.filters.can_cut = false;
            this.filters.is_carried = false;
            this.filters.is_in_desks = false;
            this.filters.can_disrupt_cameras = false;
            this.filters.is_outfit = false;
            this.filters.is_craftable = false;
            this.filters.is_illegal = false;
        }
    }
});
