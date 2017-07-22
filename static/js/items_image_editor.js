var vue_delimiters = ['${', '}']; // Because Jinja2 already uses double brackets

var app = new Vue({
    delimiters: vue_delimiters,
    el: '#app',
    data: {
        loading: true,
        image_name: '',
        wiki_images: wiki_images
    },
    mounted: function() {
        this.$nextTick(function () {
            this.loading = false;
        });
    },
    computed: {
        filteredWikiImages: function() {
            var filtered_wiki_images = {};

            for (var wiki_image_name in this.wiki_images) {
                var wiki_image = this.wiki_images[wiki_image_name];
                var match = true;

                if (this.image_name) {
                    match = (wiki_image_name.toLowerCase().indexOf(this.image_name.toLowerCase()) !== -1);
                }

                if (match) {
                    filtered_wiki_images[wiki_image_name] = wiki_image;
                }
            }

            return filtered_wiki_images;
        }
    }
});