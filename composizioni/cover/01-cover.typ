// Copyright (c) 2026 Ilya Snegov (aka Sierra Arn)
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// composizioni/cover/01-cover.typ

#let cover-page(
    collection: none,
    number: none,
    title: none,
    instruments: none,
    author: none,
    date: none,
) = {
    page(
        align(
            left + horizon,
            block(width: 90%)[
                #text(size: 1.75em, collection)

                #v(2.5em, weak: true)

                #text(size: 2.75em, strong([No. #number: #title]))

                #v(1.5em, weak: true)

                #text(size: 1.35em, emph([for #instruments]))

                #v(2em, weak: true)

                #text(size: 1.5em, author)

                #v(2em, weak: true)

                #text(size: 1em, date.display("[day] [month repr:long] [year]"))
            ],
        ),
    )
}
